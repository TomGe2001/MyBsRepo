from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
import secrets
from module.forms import FlaskForm, LoginForm, RegisterForm

db = SQLAlchemy()
app = Flask(__name__)

app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mariadb://root:@localhost:3306/bs_db'
csrf = CSRFProtect(app)
db.init_app(app)


class User(db.Model):
    __tablename__ = 'users'
    username = db.Column(db.String(40), unique=True, nullable=False, primary_key=True)
    password = db.Column(db.String(40), nullable=False)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # 查询数据库中是否有此用户
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            # TODO: 设置用户为已登录
            # login_user(user, remember=form.remember_me.data)
            # 成功信息
            flash('Logged in successfully.')
            return redirect(url_for('index'))
        # 错误信息
        flash('Invalid username or password.')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # 在数据库中创建一个新用户
        user = User(username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You can now login')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


if __name__ == '__main__':
    db.create_all()
    app.run()
