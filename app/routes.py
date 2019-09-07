
from flask import render_template, flash, redirect, url_for

from app import app
from app.forms import LoginForm

from flask_login import current_user, login_user, login_required

from app.models import User
from flask_login import logout_user
from app import  db
from app.forms import RegistrationFrom
from datetime import datetime
'''
 函数上面的两个奇怪的＠app.route行是装饰器，这是Python语言的一个独特功能。 装饰器会修改跟在其后的函数。
  装饰器的常见模式是使用它们将函数注册为某些事件的回调函数。 
  在这种情况下，＠app.route修饰器在作为参数给出的URL和函数之间创建一个关联。
   在这个例子中，有两个装饰器，它们将URL /和/index索引关联到这个函数。 这意味着，当Web浏览器请求这两个URL中的任何一个时，
 Flask将调用该函数并将其返回值作为响应传递回浏览器。这样做是为了在运行这个应用程序的时候会稍微有一点点意义。
'''

'''
将模板转换为完整的HTML页面的操作称为渲染。 为了渲染模板，需要从Flask框架中导入一个名为render_template()的函数。 
该函数需要传入模板文件名和模板参数的变量列表，并返回模板中所有占位符都用实际变量值替换后的字符串结果。
render_template()函数调用Flask框架原生依赖的Jinja2模板引擎。 Jinja2用render_template()函数传入的参数中的相应值替换{{...}}块
'''
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/')
@app.route('/index')

# @login_required
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='home', posts=posts)


'''
 当一个没有登录的用户访问被@login_required装饰器保护的视图函数时，装饰器将重定向到登录页面，
 不过，它将在这个重定向中包含一些额外的信息以便登录后的回转。
  例如，如果用户导航到*/index*，那么@login_required装饰器将拦截请求并以重定向到*/login来响应
  ，但是它会添加一个查询字符串参数来丰富这个URL，如/login?next=/index*。
   原始URL设置了next查询字符串参数后，应用就可以在登录后使用它来重定向
'''
'''
我从forms.py导入LoginForm类，并生成了一个实例传入模板。form=form的语法看起来奇怪，这是Python函数或方法传入关键字参数的方式
，左边的form代表在模板中引用的变量名称，右边则是传入的form实例。这就是获取表单字段渲染结果的所有代码了
'''

'''
methods参数。 它告诉Flask这个视图函数接受GET和POST请求，并覆盖了默认的GET。 
HTTP协议规定对GET请求需要返回信息给客户端（本例中是浏览器）。 本应用的所有GET请求都是如此。 
当浏览器向服务器提交表单数据时，通常会使用POST请求（实际上用GET请求也可以，但这不是推荐的做法）。
之前的“Method Not Allowed”错误正是由于视图函数还未配置允许POST请求。 通过传入methods参数，你就能告诉Flask哪些请求方法可以被接受
'''

'''
form.validate_on_submit()实例方法会执行form校验的工作。
当浏览器发起GET请求的时候，它返回False，这样视图函数就会跳过if块中的代码，直接转到视图函数的最后一句来渲染模板

当用户在浏览器点击提交按钮后，浏览器会发送POST请求。
form.validate_on_submit()就会获取到所有的数据，运行字段各自的验证器，全部通过之后就会返回True，这表示数据有效。
不过，一旦有任意一个字段未通过验证，这个实例方法就会返回False，引发类似GET请求那样的表单的渲染并返回给用户。
稍后我会在添加代码以实现在验证失败的时候显示一条错误消息。

当form.validate_on_submit()返回True时，登录视图函数调用从Flask导入的两个新函数。 flash()函数是向用户显示消息的有效途径。
 许多应用使用这个技术来让用户知道某个动作是否成功。我将使用这种机制作为临时解决方案，因为我没有基础架构来真正地登录用户。
  显示一条消息来确认应用已经收到登录认证凭据，我认为对当前来说已经足够了。

登录视图函数中使用的第二个新函数是redirect()。这个函数指引浏览器自动重定向到它的参数所关联的URL。
当前视图函数使用它将用户重定向到应用的主页

当你调用flash()函数后，Flask会存储这个消息，但是却不会奇迹般地直接出现在页面上。
模板需要将消息渲染到基础模板中，才能让所有派生出来的模板都能显示出来

'''
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


'''
为了更好地管理这些链接，Flask提供了一个名为url_for()的函数，它使用URL到视图函数的内部映射关系来生成URL。 
例如，url_for('login')返回/login，url_for('index')返回/index。
 url_for()的参数是endpoint名称，也就是视图函数的名字。

'''

'''
current_user变量来自Flask-Login，可以在处理过程中的任何时候调用以获取用户对象。
 这个变量的值可以是数据库中的一个用户对象（Flask-Login通过我上面提供的用户加载函数回调读取），
 或者如果用户还没有登录，则是一个特殊的匿名用户对象。 还记得那些Flask-Login必须的用户对象属性？
  其中之一是is_authenticated，它可以方便地检查用户是否登录。 当用户已经登录，我只需要重定向到主页。
  
   第一步是从数据库加载用户。 利用表单提交的username，我可以查询数据库以找到用户。
    为此，我使用了SQLAlchemy查询对象的filter_by()方法。 filter_by()的结果是一个只包含具有匹配用户名的对象的查询结果集。
     因为我知道查询用户的结果只可能是有或者没有，所以我通过调用first()来完成查询
'''

'''
如果用户名和密码都是正确的，那么我调用来自Flask-Login的login_user()函数。
 该函数会将用户登录状态注册为已登录，这意味着用户导航到任何未来的页面时，
 应用都会将用户实例赋值给current_user变量。


'''
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

#要完成应用程序，你需要在定义Flask应用程序实例的顶层（译者注：也就是microblog目录下）创建一个命名为microblog.py的Python脚本


@app.route('/register', methods = ['GET', 'Post'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationFrom()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register',form=form)
'''
这个视图函数的逻辑也是一目了然，我首先确保调用这个路由的用户没有登录。表单的处理方式和登录的方式一样。在if validate_on_submit()条件块下，
完成的逻辑如下：使用获取自表单的username、email和password创建一个新用户，将其写入数据库，然后重定向到登录页面以便用户登录。
'''


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author':user, 'body':'Test Post #1'},
        {'author':user, 'body':'Test Post #2'}
    ]
    return render_template('user.html',user=user, posts=posts)

'''
 本例中被<和>包裹的URL <username>是动态的。 当一个路由包含动态组件时，
 Flask将接受该部分URL中的任何文本，并将以实际文本作为参数调用该视图函数
 first_or_404()，当有结果时它的工作方式与first()完全相同，
 但是在没有结果的情况下会自动发送404 error给客户端
'''