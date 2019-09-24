


from flask import render_template, flash, redirect, url_for, request, current_app

from flask_login import current_user, login_user, login_required
from app.main.forms import EditProfileForm, PostForm, SearchForm
from app.models import User, Post
from app import  db
from datetime import datetime
from app.main import bp
from flask import g

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
@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()



@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('main.index'))
    page = request.args.get('page',1,type=int)
    posts = current_user.followed_posts().paginate(
        page,current_app.config['POSTS_PER_PAGE'], False
    )
    next_url = url_for('main.index', page=posts.next_num) \
    if posts.has_next else None
    prev_url = url_for('main.index', page = posts.prev_num) \
    if posts.has_prev else None
    return render_template('index.html', title='home', form=form, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


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


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page',1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page,current_app.config['POSTS_PER_PAGE'],False
    )
    next_url = url_for('main.user',username=user.username, page=posts.next_num) \
    if posts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) \
    if posts.has_prev else None
    return render_template('user.html',user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)

'''
 本例中被<和>包裹的URL <username>是动态的。 当一个路由包含动态组件时，
 Flask将接受该部分URL中的任何文本，并将以实际文本作为参数调用该视图函数
 first_or_404()，当有结果时它的工作方式与first()完全相同，
 但是在没有结果的情况下会自动发送404 error给客户端
'''


@bp.route('/edit_profile', methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('main.edit_profile'))
    elif request.method =='GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',form=form)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    if username == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('main.user', username=username))


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page',1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False
    )
    next_url = url_for('main.explore', page=posts.next_num) \
    if posts.has_next else None
    prev_url = url_for('main.explore', page = posts.prev_num) \
    if posts.has_prev else None
    return render_template('index.html',title='Explore', posts=posts.items,
                           next_url=next_url, prev_url=prev_url)

'''
Flask-SQLAlchemy的paginate()方法原生就支持分页。例如，我想要获取用户关注的前20个动态，
我可以将all()结束调用替换成如下的查询：

>>> user.followed_posts().paginate(1, 20, False).items
'''

@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data,page = page+1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data,page = page-1) \
        if page>1 else None
    return render_template('search.html',title='Search',posts=posts,
                           next_url=next_url, prev_url=prev_url)
