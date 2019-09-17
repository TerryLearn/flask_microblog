
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired,ValidationError, Email, EqualTo, Length
from app.models import User

'''
你在一些字段中看到的可选参数validators用于验证输入字段是否符合预期。
DataRequired验证器仅验证字段输入是否为空
'''
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    remember_me = BooleanField('Remeber Me')
    submit = SubmitField('Sign In')


class RegistrationFrom(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a diffent username')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a diffent email')


'''
首先，对于email字段，我在DataRequired之后添加了第二个验证器，名为Email。
 这个来自WTForms的另一个验证器将确保用户在此字段中键入的内容与电子邮件地址的结构相匹配。

由于这是一个注册表单，习惯上要求用户输入密码两次，以减少输入错误的风险。 
出于这个原因，我提供了password和password2字段。 第二个password字段使用另一个名为EqualTo的验证器，它将确保其值与第一个password字段的值相同。

我还为这个类添加了两个方法，名为validate_username()和validate_email()。 
当添加任何匹配模式validate_ <field_name>的方法时，WTForms将这些方法作为自定义验证器，并在已设置验证器之后调用它们。
 本处，我想确保用户输入的username和email不会与数据库中已存在的数据冲突，所以这两个方法执行数据库查询，并期望结果集为空。
  否则，则通过ValidationError触发验证错误

'''


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0,max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username')

'''
我在这个表单中使用了一个新的字段类型和一个新的验证器。
 对于“about_me”字段，我使用TextAreaField，这是一个多行输入文本框，用户可以在其中输入文本。 
 为了验证这个字段的长度，我使用了Length，它将确保输入的文本在0到140个字符之间，
 因为这是我为数据库中的相应字段分配的空间。
'''


class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')
