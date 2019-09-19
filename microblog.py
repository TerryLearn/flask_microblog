
from app import app

# @app.shell_context_processor
# def make_shell_context():
#     return {'db': db, 'User': User, 'Post': Post}
'''
还记得两个app实体吗？ 在这里，你可以在同一句话中看到两者。 Flask应用程序实例被称为app，是app包的成员。
from app import app语句从app包导入其成员app变量。 如果你觉得这很混乱，你可以重命名包或者变量
'''
app.run(host='0.0.0.0',debug=True)