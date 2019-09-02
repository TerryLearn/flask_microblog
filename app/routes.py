from flask import render_template

from app import app

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


#要完成应用程序，你需要在定义Flask应用程序实例的顶层（译者注：也就是microblog目录下）创建一个命名为microblog.py的Python脚本