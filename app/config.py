import  os

basedir = os.path.abspath(os.path.dirname(__file__))


'''
SECRET_KEY是我添加的唯一配置选项，对大多数Flask应用来说，它都是极其重要的。
Flask及其一些扩展使用密钥的值作为加密密钥，用于生成签名或令牌。
Flask-WTF插件使用它来保护网页表单免受名为Cross-Site Request Forgery或CSRF（发音为“seasurf”）的恶意攻击。
顾名思义，密钥应该是隐密的，因为由它产生的令牌和签名的加密强度保证，取决于除了可信维护者之外，没有任何人能够获得它。
'''

'''
在开发阶段，安全性要求较低，因此可以直接使用硬编码字符串。
但是，当应用部署到生产服务器上的时候，我将设置一个独一无二且难以揣摩的环境变量，
这样，服务器就拥有了一个别人未知的安全密钥了
'''

'''
Flask-SQLAlchemy插件从SQLALCHEMY_DATABASE_URI配置变量中获取应用的数据库的位置。
首先从环境变量获取配置变量，未获取到就使用默认值，这样做是一个好习惯。
 本处，我从DATABASE_URL环境变量中获取数据库URL，
 如果没有定义，我将其配置为basedir变量表示的应用顶级目录下的一个名为app.db的文件路径。

SQLALCHEMY_TRACK_MODIFICATIONS配置项用于设置数据发生变更之后是否发送信号给应用，
我不需要这项功能，因此将其设置为False。
'''
class Config():
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you will never guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False