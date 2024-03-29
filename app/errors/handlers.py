

from flask import render_template
from app import db
from app.errors import bp

@bp.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


'''
 对于这两个错误，我将返回各自模板的内容。 
 请注意这两个函数在模板之后返回第二个值，这是错误代码编号。
  对于之前我创建的所有视图函数，我不需要添加第二个返回值，因为我想要的是默认值200（成功响应的状态码）。
  本处，这些是错误页面，所以我希望响应的状态码能够反映出来
'''