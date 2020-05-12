import datetime

from flask import Flask, json, request
from werkzeug.exceptions import abort

from data import db_session
from flask import render_template
from data.users import User
from data.news import News
from data.favourite_posts import FavouritePosts
from forms import LoginForm, RegisterForm, NewsForm, EditProfileForm
from flask import redirect
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
import psycopg2
import os

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    db_session.global_init("db/blogs.sqlite")
    port = int(os.environ.get("PORT", 5000))
    app.run()#host='0.0.0.0', port=port)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/", methods=['GET', 'POST'])
def new():
    count_of_my_posts = 0
    form = None
    loginform = None
    session = db_session.create_session()
    date = datetime.date.today()
    news = session.query(News).filter(News.is_private != True, News.created_date == str(date))
    count_of_posts = len(list(news))
    if current_user.is_anonymous:
        loginform = LoginForm()
        if loginform.validate_on_submit():
            session = db_session.create_session()
            user = session.query(User).filter(User.email == loginform.email.data).first()
            if user and user.check_password(loginform.password.data):
                login_user(user, remember=loginform.remember_me.data)
                return redirect("/")

        form = RegisterForm()
        if form.validate_on_submit():
            if form.password.data != form.password_again.data:
                return render_template('posts.html',
                                       form=form, loginform=loginform, news=news, title='Посты за сегодняшний день',
                                       message="Пароли не совпадают", count_of_posts=count_of_posts)
            session = db_session.create_session()
            if session.query(User).filter(User.email == form.email.data).first() or \
                    session.query(User).filter(User.name == form.name.data).first():
                return render_template('posts.html',
                                       form=form, loginform=loginform, news=news, title='Посты за сегодняшний день',
                                       message="Такой пользователь уже есть", count_of_posts=count_of_posts)
            user = User(
                name=form.name.data,
                email=form.email.data
            )
            user.set_password(form.password.data)
            session.add(user)
            session.commit()
            login_user(user, remember=True)
            return redirect('/')

    return render_template("posts.html", news=news[::-1], form=form, loginform=loginform,
                           title='Посты за сегодняшний день',
                           count_of_posts=count_of_posts)


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/allposts", methods=['GET', 'POST'])
def allposts():
    count_of_my_posts = 0
    form = None
    loginform = None
    session = db_session.create_session()
    news = session.query(News).filter(News.is_private != True)
    count_of_posts = len(list(news))
    if current_user.is_anonymous:
        loginform = LoginForm()
        if loginform.validate_on_submit():
            session = db_session.create_session()
            user = session.query(User).filter(User.email == loginform.email.data).first()
            if user and user.check_password(loginform.password.data):
                login_user(user, remember=loginform.remember_me.data)
                session.close()
                return redirect("/")

        form = RegisterForm()
        if form.validate_on_submit():
            if form.password.data != form.password_again.data:
                return render_template('posts.html',
                                       form=form, loginform=loginform, news=news, title='Посты за всё время',
                                       message="Пароли не совпадают", count_of_posts=count_of_posts)
            session = db_session.create_session()
            if session.query(User).filter(User.email == form.email.data).first() or \
                    session.query(User).filter(User.name == form.name.data).first():
                return render_template('posts.html',
                                       form=form, loginform=loginform, news=news, title='Посты за всё время',
                                       message="Такой пользователь уже есть", count_of_posts=count_of_posts)
            user = User(
                name=form.name.data,
                email=form.email.data
            )
            user.set_password(form.password.data)
            session.add(user)
            session.commit()
            return redirect('/')

    return render_template("posts.html", news=news[::-1], form=form, loginform=loginform, title='Посты за всё время',
                           count_of_posts=count_of_posts)


@app.route('/addpost', methods=['GET', 'POST'])
@login_required
def add_post():
    form = NewsForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.description = form.description.data
        news.content = form.content.data
        news.tags = form.tags.data
        news.is_private = form.is_private.data
        date = datetime.date.today()
        news.created_date = date
        current_user.news.append(news)
        session.merge(current_user)
        session.commit()
        return redirect("/")
    return render_template('adding.html',
                           form=form)


@app.route('/editpost/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        session = db_session.create_session()
        news = session.query(News).filter(News.id == id,
                                          News.user == current_user).first()
        if news or current_user.is_admin:
            form.title.data = news.title
            form.description.data = news.description
            form.content.data = news.content
            form.tags.data = news.tags
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        news = session.query(News).filter(News.id == id,
                                          News.user == current_user).first()
        if news or current_user.is_admin:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            session.commit()
            return redirect('/')
        else:
            abort(404)

    return render_template('adding.html', form=form)


@app.route('/postdelete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    session = db_session.create_session()
    news = session.query(News).filter(News.id == id and
                                      News.user == current_user).first()
    if news or current_user.is_admin:
        session.delete(news)
        session.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/favbtn/<int:id>', methods=['GET', 'POST'])
@login_required
def addfavourite(id):
    session = db_session.create_session()
    post = session.query(News).filter(News.id == id).first()
    if not session.query(FavouritePosts).filter(FavouritePosts.user_id == current_user.id,
                                                FavouritePosts.post_id == post.id).first():
        favpost = FavouritePosts(
            post_id=post.id,
            title=post.title,
            description=post.description,
            content=post.content,
            created_date=post.created_date,
            tags=post.tags,
            author_name=post.user.name,
            user_id=current_user.id
        )
        current_user.favourite_posts.append(favpost)
        session.merge(current_user)
        session.commit()
        return redirect('/favourite')
    else:
        favpost = session.query(FavouritePosts).filter(FavouritePosts.post_id == post.id, FavouritePosts.user_id ==
                                                       current_user.id).first()
        session.delete(favpost)
        session.commit()
        return redirect('/favourite')


@app.route('/favourite', methods=['GET', 'POST'])
def favourite():
    session = db_session.create_session()
    posts = current_user.favourite_posts
    count_of_posts = len(list(posts))

    return render_template("favourite.html", news=posts[::-1], title='Избранные посты', count_of_posts=count_of_posts,
                           )


@app.route('/user/<int:id>', methods=['GET', 'POST'])
def profile(id):
    session = db_session.create_session()
    user = session.query(User).filter(User.id == id).first()
    if not user:
        abort(404)
    count_of_my_posts = len(list(session.query(News).filter(News.user == user)))
    if user == current_user:
        news = user.news
    else:
        news = session.query(News).filter(News.user == user, News.is_private != True)
    return render_template('profile.html', title='Профиль', count_of_my_posts=count_of_my_posts,
                           user=user, news=news[::-1])


@app.route('/user/<int:id>/edit', methods=["GET", "POST"])
def editProfile(id):
    form = EditProfileForm()
    if request.method == "GET":
        session = db_session.create_session()
        user = session.query(User).filter(User.id == id).first()
        if user and user == current_user:
            form.name.data = user.name
            form.about_me.data = user.about_me
            form.status.data = user.status
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.id == id).first()
        if user and user == current_user:
            user.name = form.name.data
            user.status = form.status.data
            user.about_me = form.about_me.data
            session.commit()
            return redirect('/')
        else:
            abort(404)

    return render_template('editProfile.html', form=form)


if __name__ == '__main__':
    main()
