

from flask import render_template, flash, redirect, url_for

from app.auth import bp

from flask_login import current_user, login_user

from app.models import User
from flask_login import logout_user
from app import  db
from app.auth.forms import RegistrationFrom, LoginForm
from app.auth.forms import ResetPasswordRequestForm, ResetPasswordForm
from app.auth.email import send_password_reset_email


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('main.index'))
    return render_template('auth/login.html', title='Sign In', form=form)


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
@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


# 要完成应用程序，你需要在定义Flask应用程序实例的顶层（译者注：也就是microblog目录下）创建一个命名为microblog.py的Python脚本


@bp.route('/register', methods = ['GET', 'Post'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationFrom()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register' ,form=form)


'''
这个视图函数的逻辑也是一目了然，我首先确保调用这个路由的用户没有登录。表单的处理方式和登录的方式一样。在if validate_on_submit()条件块下，
完成的逻辑如下：使用获取自表单的username、email和password创建一个新用户，将其写入数据库，然后重定向到登录页面以便用户登录。
'''

@bp.route('/reset_password_request',methods=['GET','POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            # test_send()
            flash('Check your email for the instructions to reset your password')
            return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', title='Reset Password',form=form)


@bp.route('/reset_password/<token>', methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html',form=form)

