from flask import Flask, render_template, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from forms import LoginForm, RegisterForm
from models import User, db, app

app.config["SECRET_KEY"] = "12345678"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        session['user'] = data['account']
        flash("登录成功", "ok")
        return redirect("/art/list/1")
    # 返回登录template
    return render_template("login.html", title="login", form=form)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        data = form.data
        # 保存数据
        user = User(
            account=data["account"],
            # 对于pwd进行加密
            pwd=generate_password_hash(data["pwd"]),
        )
        db.session.add(user)
        db.session.commit()
        # 定义一个会话的闪现
        flash("注册成功, 请登录", "ok")
    return render_template("register.html", title="注册", form=form)


@app.route('/jump')
def jump():
    return render_template('main.html')


@app.route('/reset')
def reset():
    return render_template('reset.html')


if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=8080)
