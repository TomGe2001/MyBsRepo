import os
import uuid
from datetime import datetime
from functools import wraps

from flask import render_template, redirect, flash, session, url_for, request
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

from forms import LoginForm, RegisterForm, ArticleAddForm, ArticleEditForm
from models import User, db, app, Article

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


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        session['user'] = data['account']
        flash("登录成功", "ok")
        return redirect(url_for('go_base'))
    # 返回登录template
    return render_template("login.html", title="login", form=form)


# logout 用户退出(302跳转到登录页面)
@app.route("/logout/", methods=["GET"])  # 用户退出
@user_login_req
def logout():
    # 重定向到指定的视图对应url，蓝图中才可以使用
    # return redirect(url_for("app.login"))
    # 调用session的pop功能将user变为None
    session.pop("user", None)
    # 直接跳转路径
    return redirect("/login/")


@app.route('/base', endpoint='go_base')
def go_base():
    return render_template('art_base.html')


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


# 修改文件名称
def change_name(name):
    # 获取后缀名
    info = os.path.splitext(name)
    # 文件名: 时间格式字符串+唯一字符串+后缀名
    name = datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + info[-1]
    return name


# art_add 发布文章
@app.route("/art/add/", methods=["GET", "POST"])  # 发布文章\
@user_login_req
def art_add():
    form = ArticleAddForm()
    if form.validate_on_submit():
        data = form.data

        # 上传logo
        file = secure_filename(form.logo.data.filename)
        logo = change_name(file)
        if not os.path.exists(app.config["uploads"]):
            os.makedirs(app.config["uploads"])
        # 保存文件
        form.logo.data.save(app.config["uploads"] + "/" + logo)
        # 获取用户ID
        user = User.query.filter_by(account=session["user"]).first()
        user_id = user.id
        # 保存数据，Article
        article = Article(
            title=data["title"],
            category=data["category"],
            user_id=user_id,
            logo=logo,
            content=data["content"],
            add_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        db.session.add(article)
        db.session.commit()
        flash(u"发布文章成功", "ok")
    return render_template("art_add.html", title="发布文章", form=form)


# art_edit 编辑文章
# 传入整型id参数
@app.route("/art/edit/<int:id>/", methods=["GET", "POST"])  # 编辑文章
@user_login_req
def art_edit(id):
    form = ArticleEditForm()
    article = Article.query.get_or_404(int(id))
    if request.method == "GET":
        form.content.data = article.content
        form.category.data = article.category
    # 莫名其妙赋初值:不赋初值表单提交时会提示封面为空
    # 放在这里修复显示请选择封面的错误
    form.logo.data = article.logo
    if form.validate_on_submit():
        data = form.data
        # 上传logo
        file = secure_filename(form.logo.data.filename)
        logo = change_name(file)
        if not os.path.exists(app.config["uploads"]):
            os.makedirs(app.config["uploads"])
        # 保存文件
        form.logo.data.save(app.config["uploads"] + "/" + logo)
        article.logo = logo
        article.title = data['title']
        article.content = data['content']
        article.category = data['category']
        db.session.add(article)
        db.session.commit()
        flash(u"编辑文章成功", "ok")
    return render_template("art_edit.html", form=form, title="编辑文章", article=article)


# art_list 文章列表
@app.route("/art/list/<int:page>/", methods=["GET"])  # 文章列表
@user_login_req
def art_list(page):
    if page is None:
        page = 1
    # 只展示当前用户才能看到的内容
    user = User.query.filter_by(account=session["user"]).first()
    user_id = user.id
    page_data = Article.query.filter_by(
        user_id=user_id
    ).order_by(
        Article.add_time.desc()
    ).paginate(page=page, per_page=1)
    category = [(1, u"科技"), (2, u"搞笑"), (3, u"军事")]
    return render_template("art_list.html", title="文章列表", page_data=page_data, category=category)


# art_del 删除文章
@app.route("/art/del/<int:id>/", methods=["GET"])  # 删除文章
@user_login_req
def art_del(id):
    article = Article.query.get_or_404(int(id))
    db.session.delete(article)
    db.session.commit()
    flash("删除《%s》成功!" % article.title, "ok")
    return redirect("/art/list/1")


if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=8080)
