from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo


# 使用Flask-WTF和WTForms库定义了一个名为'LoginForm'的表单类。
# 添加了Email、Password和RememberMe三个输入框。
# 采用了WTForms中提供的验证器来验证用户所输入的值是否合法。
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(8)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8)])


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(8)])

    # TODO：注册功能中的确认密码
    # password = PasswordField('Password', validators=[DataRequired(), Length(min=6), EqualTo('confirm_password', message='Passwords must match')])

    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])