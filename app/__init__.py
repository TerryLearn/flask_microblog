
from flask import Flask
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)

app.config.from_object(Config)
print(app.config['SECRET_KEY'])
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

'''
上面的'login'值是登录视图函数（endpoint）名，换句话说该名称可用于url_for()函数的参数并返回对应的URL。

Flask-Login使用名为@login_required的装饰器来拒绝匿名用户的访问以保护某个视图函数。
 当你将此装饰器添加到位于@app.route装饰器下面的视图函数上时，该函数将受到保护，不允许未经身份验证的用户访问。 以下是该装饰器如何应用于应用的主页视图函数的案例：
'''

'''
上面的脚本仅仅是从flask中导入的类Flask，并以此类创建了一个应用程序对象
传递给Flask类的__name__变量是一个Python预定义的变量，它表示当前调用它的模块的名字
其一，这里有两个实体名为app。 app包由app目录和__init__.py脚本来定义构成，
并在from app import routes语句中被引用。 app变量被定义为__init__.py脚本中的Flask类的一个实例，以至于它成为app包的属性

其二，routes模块是在底部导入的，而不是在脚本的顶部。 最下面的导入是解决循环导入的问题，这是Flask应用程序的常见问题。
 你将会看到routes模块需要导入在这个脚本中定义的app变量，因此将routes的导入放在底部可以避免由于这两个文件之间的相互引用而导致的错误
'''

from app import  routes, models


'''
那么在routes模块中有些什么？ 路由是应用程序实现的不同URL。 在Flask中，应用程序路由的处理逻辑被编写为Python函数，
称为视图函数。 视图函数被映射到一个或多个路由URL，以便Flask知道当客户端请求给定的URL时执行什么逻辑
'''

