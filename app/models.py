
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64),index=True, unique=True)
    email = db.Column(db.String(120),index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)


'''
上面创建的User类继承自db.Model，它是Flask-SQLAlchemy中所有模型的基类。
 这个类将表的字段定义为类属性，字段被创建为db.Column类的实例，
 它传入字段类型以及其他可选参数，例如，可选参数中允许指示哪些字段是唯一的并且是可索引的，
 这对高效的数据检索十分重要

'''