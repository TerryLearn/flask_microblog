
from  datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
from time import time
import jwt
from app import db,login
from flask import current_app
from app.search import add_to_index, remove_from_index, query_index


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

'''
这种关系将User实例关联到其他User实例，所以按照惯例，对于通过这种关系关联的一对用户来说，左侧用户关注右侧用户。 
我在左侧的用户中定义了followed的关系，因为当我从左侧查询这个关系时，我将得到已关注的用户列表（即右侧的列表）。
 让我们逐个检查这个db.relationship()所有的参数：

'User'是关系当中的右侧实体（将左侧实体看成是上级类）。由于这是自引用关系，所以我不得不在两侧都使用同一个实体。
secondary 指定了用于该关系的关联表，就是使用我在上面定义的followers。
primaryjoin 指明了通过关系表关联到左侧实体（关注者）的条件 。关系中的左侧的join条件是关系表中的follower_id字段与这个关注者的用户ID匹配。
followers.c.follower_id表达式引用了该关系表中的follower_id列。
secondaryjoin 指明了通过关系表关联到右侧实体（被关注者）的条件 。
 这个条件与primaryjoin类似，唯一的区别在于，现在我使用关系表的字段的是followed_id了。
backref定义了右侧实体如何访问该关系。在左侧，关系被命名为followed，所以在右侧我将使用followers来表示所有左侧用户的列表，即粉丝列表。
附加的lazy参数表示这个查询的执行模式，设置为动态模式的查询不会立即执行，直到被调用，这也是我设置用户动态一对多的关系的方式。
lazy和backref中的lazy类似，只不过当前的这个是应用于左侧实体，backref中的是应用于右侧实体

'''
followers = db.Table('followers',
                     db.Column('follower_id', db.Integer,db.ForeignKey('user.id')),
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id'))
                     )

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64),index=True, unique=True)
    email = db.Column(db.String(120),index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship('User',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.follower_id == id),
                               backref= db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash,password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'http://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.follower_id == user.id).count() > 0

    def followed_posts(self):
        followed =  Post.query.join(
            followers, (followers.c.follower_id==Post.user_id)).filter(
            followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password':self.id,'ext':time()+expires_in},
                          current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


    def __repr__(self):
        return '<User {}>'.format(self.username)


'''
Post.query.join(...).filter(...).order_by(...)
复杂的查询
我在用户动态表上调用join操作。 第一个参数是followers关联表，第二个参数是join条件。 
我的这个调用表达的含义是我希望数据库创建一个临时表，它将用户动态表和关注者表中的数据结合在一起。 数据将根据参数传递的条件进行合并。

我使用的条件表示了followers关系表的followed_id字段必须等于用户动态表的user_id字段。 
要执行此合并，数据库将从用户动态表（join的左侧）获取每条记录，并追加followers关系表（join的右侧）中的匹配条件的所有记录。
 如果followers关系表中有多个记录符合条件，那么用户动态数据行将重复出现。 
 如果对于一个给定的用户动态，followers关系表中却没有匹配，那么该用户动态的记录不会出现在join操作的结果中
 
 filter(followers.c.follower_id == self.id)
该查询是User类的一个方法，self.id表达式是指我感兴趣的用户的ID。
filter()挑选临时表中follower_id列等于这个ID的行，换句话说，我只保留follower(粉丝)是该用户的数据。
'''
'''
我在is_following()中使用的过滤条件是，查找关联表中左侧外键设置为self用户且右侧设置为user参数的数据行。 
查询以count()方法结束，返回结果的数量。 这个查询的结果是0或1，因此检查计数是1还是大于0实际上是相等的。
'''
'''
上面创建的User类继承自db.Model，它是Flask-SQLAlchemy中所有模型的基类。
 这个类将表的字段定义为类属性，字段被创建为db.Column类的实例，
 它传入字段类型以及其他可选参数，例如，可选参数中允许指示哪些字段是唯一的并且是可索引的，
 这对高效的数据检索十分重要

'''

class Post(SearchableMixin, db.Model):
    __searchable__=['body']
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __repr__(self):
        return '<Post {}>'.format(self.body)


'''
新的“Post”类表示用户发表的动态。 timestamp字段将被编入索引，如果你想按时间顺序检索用户动态，这将非常有用。
 我还为其添加了一个default参数，并传入了datetime.utcnow函数。
  当你将一个函数作为默认值传入后，SQLAlchemy会将该字段设置为调用该函数的值（请注意，在utcnow之后我没有包含()，所以我传递函数本身，而不是调用它的结果）。
   通常，在服务应用中使用UTC日期和时间是推荐做法。 这可以确保你使用统一的时间戳，无论用户位于何处，这些时间戳会在显示时转换为用户的当地时间

user_id字段被初始化为user.id的外键，这意味着它引用了来自用户表的id值。本处的user是数据库表的名称，Flask-SQLAlchemy自动设置类名为小写来作为对应表的名称。
 User类有一个新的posts字段，用db.relationship初始化。这不是实际的数据库字段，而是用户和其动态之间关系的高级视图，因此它不在数据库图表中。
 对于一对多关系，db.relationship字段通常在“一”的这边定义，并用作访问“多”的便捷方式。因此，如果我有一个用户实例u，
 表达式u.posts将运行一个数据库查询，返回该用户发表过的所有动态。 db.relationship的第一个参数表示代表关系“多”的类。
  backref参数定义了代表“多”的类的实例反向调用“一”的时候的属性名称。这将会为用户动态添加一个属性post.author，调用它将返回给该用户动态的用户实例。
   lazy参数定义了这种关系调用的数据库查询是如何执行的
   
   一旦我变更了应用模型，就需要生成一个新的数据库迁移：

(venv) $ flask db migrate -m "posts table"
并将这个迁移应用到数据库：
(venv) $ flask db upgrade
'''


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

'''
使用Flask-Login的@login.user_loader装饰器来为用户加载功能注册函数。
 Flask-Login将字符串类型的参数id传入用户加载函数，
 因此使用数字ID的数据库需要如上所示地将字符串转换为整数。


'''
