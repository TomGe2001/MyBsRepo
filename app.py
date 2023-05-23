import os

from functools import wraps

from flask import render_template, redirect, flash, session, url_for, request
from sqlalchemy import text
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

from decorators import login_required
from forms import LoginForm, RegisterForm
from models import User, db, app, Question, Answer

app.config["SECRET_KEY"] = "12345678"
# 设置上传封面图路径
app.config["uploads"] = os.path.join(os.path.dirname(__file__), "static/uploads")


# 登录装饰器
def user_login_req(f):
    @wraps(f)
    def login_req(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)

    return login_req


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/jump')
def jump():
    return render_template('main.html')


@app.route('/bbs')
def bbs_index():
    context = {
        'questions': Question.query.order_by('create_time').all()
    }
    return render_template('bbsPage/bbs_index.html', **context)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == 'GET':
        return render_template('login.html', form=form)
    else:
        username = request.form.get('account')
        password = request.form.get('pwd')
    if form.validate_on_submit():
        data = form.data
        session['user_id'] = data.get('account')
        return redirect(url_for('bbs_index'))
    # 返回登录template
    return render_template("login.html", title="login", form=form)


# logout 用户退出(302跳转到登录页面)
@app.route("/logout/", methods=["GET"])  # 用户退出
def logout():
    # 调用session的pop功能将user变为None
    session.pop("user", None)
    # 直接跳转路径
    return redirect(url_for('index'))


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


@app.route('/question/', methods=['GET', 'POST'])
@login_required
def question():
    if request.method == 'GET':
        return render_template('bbsPage/question.html')
    else:
        title = request.form.get('title')
        content = request.form.get('content')
        question = Question(title=title, content=content)
        user_id = session.get('user_id')
        user = User.query.filter(User.id == user_id).first()
        question.author = user
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('bbs_index'))


@app.route('/detail/<question_id>')
def detail(question_id):
    question_model = Question.query.filter(Question.id == question_id).first()
    return render_template('bbsPage/detail.html', question=question_model, question_count=len(question_model.answers))


@app.route('/add_answer/', methods=['POST'])
@login_required
def add_answer():
    content = request.form.get('answer_content')
    question_id = request.form.get('question_id')

    answer = Answer(content=content)
    user_id = session['user_id']
    user = User.query.filter(User.id == user_id).first()
    answer.author = user
    question = Question.query.filter(Question.id == question_id).first()
    answer.question = question
    db.session.add(answer)
    db.session.commit()
    return redirect(url_for('detail', question_id=question_id))


@app.route('/search/', methods=['POST'])
def search():
    search_key = request.form.get('search_key')
    context = {
        # 'questions': Question.query.filter(Question.title.contains(search_key)).order_by('-create_time').all()
        'questions': Question.query.filter(Question.title.contains(search_key)).order_by(text('-create_time')).all()

    }
    return render_template('bbsPage/bbs_index.html', **context)


if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=8080)
