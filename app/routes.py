
from flask import render_template, flash, redirect, url_for

from app import app
from app.forms import LoginForm

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
@app.route('/')
@app.route('/index')

def index():
    user = {'username': 'Terry--'}
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
    return render_template('index.html', title='home', user=user, posts=posts)


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
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me=()'.format(form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


'''
为了更好地管理这些链接，Flask提供了一个名为url_for()的函数，它使用URL到视图函数的内部映射关系来生成URL。 
例如，url_for('login')返回/login，url_for('index')返回/index。
 url_for()的参数是endpoint名称，也就是视图函数的名字。

'''
#要完成应用程序，你需要在定义Flask应用程序实例的顶层（译者注：也就是microblog目录下）创建一个命名为microblog.py的Python脚本