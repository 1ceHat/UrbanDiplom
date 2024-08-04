from flask import Flask, request, redirect, url_for
from flask.templating import render_template

from flask_wtf import CSRFProtect
from app.forms import *

from flask_paginate import Pagination
from app.databases.db_init import *

app = Flask(__name__, template_folder='app\\templates')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
db.init_app(app=app)
alembic_.init_app(app=app)

csrf = CSRFProtect(app)
app.config['SECRET_KEY'] = '123erfghju76tresxcvbnmkuytrdFGzhGFTREFty76'
curr_user = None


@app.route('/')
def main_page():
    global curr_user
    context = {
        'user': curr_user,
    }
    return render_template('main_page.html', **context)


@app.route('/signup', methods=['GET', 'POST'])
def signup_page():
    global curr_user
    info = {}
    form = SignupForm()
    if not curr_user and request.method == 'POST':
        if form.validate_on_submit():
            user = db.session.scalars(db.select(Buyer).where(Buyer.name == form.username.data)).first()
            if user is not None:
                info.update({'error': 'Такой пользователь уже существует',
                             'message': 'У вас уже есть аккаунт?',
                             'login': 'Авторизуйтесь!'})
            elif form.password.data != form.repeat_password.data:
                info.update({'error': 'Пароли не совпадают'})
            else:
                db.session.execute(db.insert(Buyer).values(name=form.username.data,
                                                           password=form.username.data,
                                                           age=form.age.data))
                db.session.commit()
                curr_user = db.session.scalars(db.select(Buyer).where(Buyer.name == form.username.data)).first()
                return redirect('/')

    context = {
        'info': info,
        'user': curr_user,
        'form': form,
    }
    return render_template('registration_page.html', **context)


@app.route('/login', methods=['get', 'post'])
def login_page():
    global curr_user
    info = {}
    form = LoginForm(request.form)
    if not curr_user and request.method == 'POST':
        if form.validate_on_submit():
            user = db.session.scalars(db.select(Buyer).where(Buyer.name == form.username.data)).first()
            if user is None:
                info.update({'error': 'Такого пользователя не существует',
                             'message': 'У вас ещё нет аккаунта?',
                             'signup': 'Зарегистрируйтесь!'})
            elif form.password.data != user.password:
                info.update({'error': 'Неверный пароль'})
            else:
                curr_user = user
                return redirect(url_for('main_page'))
    context = {
        'info': info,
        'user': curr_user,
        'form': form,
    }
    return render_template('login_page.html', **context)


@app.route('/shop', methods=['get', 'post'])
def shop_page():
    global curr_user
    # technical variabals
    games = db.session.scalars(db.select(Game)).all()
    info = {}
    form = GameBuyForm()

    # variabals for paginate
    size = 3 if request.args.get('size') is None else int(request.args.get('size'))
    page = 1 if request.args.get('page') is None else int(request.args.get('page'))
    sliced_games = games[page*size-size:page*size]
    paginated_games = Pagination(total=len(games), per_page=size, page=page)

    if curr_user and request.method == 'POST':
        if form.validate_on_submit():
            game = db.session.scalars(db.select(Game).where(Game.title == form.game_title.data)).first()
            curr_user = db.session.get(Buyer, curr_user.id)
            if curr_user.balance < game.cost:
                info.update({'error': 'Недостаточно средств!'})
            elif game.age_limited and curr_user.age < 18:
                info.update({'error': 'Вы не достигли возраста'})
            elif game in curr_user.buyers_game:
                info.update({'error': 'У вас уже куплена эта игра'})
            else:
                curr_user.balance -= game.cost
                curr_user.buyers_game.append(game)
                db.session.commit()
    elif not curr_user:
        info.update({'error': 'Войдите в аккаунт!'})
    context = {
        'user': curr_user,
        'info': info,
        'games': sliced_games,
        'p_games': paginated_games,
        'size': size,
        'page': page,
        'form': form,
    }
    return render_template('shop_page.html', **context)


@app.route('/purchased_applications')
def users_game_page():
    global curr_user
    applications = []

    if curr_user:
        curr_user = db.session.get(Buyer, curr_user.id)
        applications = curr_user.buyers_game

    context = {
        'user': curr_user,
        'applications': applications,
    }
    return render_template('users_game_page.html', **context)


if __name__ == '__main__':
    app.run()
