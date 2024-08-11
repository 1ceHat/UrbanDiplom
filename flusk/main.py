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
    error = {}
    form = SignupForm()
    if not curr_user and request.method == 'POST':
        if form.validate_on_submit():
            user = db.session.scalars(db.select(Buyer).where(Buyer.name == form.username.data)).first()
            if user is not None:
                error.update({'error': 'Такой пользователь уже существует'})
            elif form.password.data != form.repeat_password.data:
                error.update({'error': 'Пароли не совпадают'})
            else:
                db.session.execute(db.insert(Buyer).values(name=form.username.data,
                                                           password=form.username.data,
                                                           age=form.age.data))
                db.session.commit()
                curr_user = db.session.scalars(db.select(Buyer).where(Buyer.name == form.username.data)).first()
                return redirect('/')

    context = {
        'error': error,
        'user': curr_user,
        'form': form,
    }
    return render_template('registration_page.html', **context)


@app.route('/login', methods=['get', 'post'])
def login_page():
    global curr_user
    error = {}
    form = LoginForm(request.form)
    if not curr_user and request.method == 'POST':
        if form.validate_on_submit():
            user = db.session.scalars(db.select(Buyer).where(Buyer.name == form.username.data)).first()
            if user is None:
                error.update({'error': 'Такого пользователя не существует'})
            elif form.password.data != user.password:
                error.update({'error': 'Неверный пароль'})
            else:
                curr_user = user
                return redirect(url_for('main_page'))
    context = {
        'error': error,
        'user': curr_user,
        'form': form,
    }
    return render_template('login_page.html', **context)


@app.route('/shop/', methods=['get', 'post'])
def shop_page():
    global curr_user
    # technical variabals
    games = db.session.scalars(db.select(Game)).all()
    info = {}
    error = {}
    form = GameBuyForm()

    # variabals for paginate
    size = 3 if request.args.get('size') is None else int(request.args.get('size'))
    page = 1 if request.args.get('page') is None else int(request.args.get('page'))
    sliced_games = games[page*size-size:page*size]
    paginated_games = Pagination(total=len(games), per_page=size, page=page)
    if len(paginated_games.pages) < page:
        sliced_games = games[len(paginated_games.pages)*size-size:len(paginated_games.pages)*size]
        paginated_games = Pagination(total=len(games), per_page=size, page=len(paginated_games.pages))

    if curr_user and request.method == 'POST':
        if form.validate_on_submit():
            game = db.session.scalars(db.select(Game).where(Game.id == form.game_id.data)).first()
            curr_user = db.session.get(Buyer, curr_user.id)
            if curr_user.balance < game.cost:
                error.update({'error': 'Недостаточно средств!'})
            elif game.age_limited and curr_user.age < 18:
                error.update({'error': 'Вы не достигли возраста'})
            elif game in curr_user.buyers_game:
                error.update({'error': 'У вас уже куплена эта игра'})
            else:
                info.update({'message': f'{game.title} куплена!'})
                curr_user.balance -= game.cost
                curr_user.buyers_game.append(game)
                db.session.commit()
    elif not curr_user:
        error.update({'error': 'Войдите в аккаунт или зарегистрируйтесь!'})
    context = {
        'user': curr_user,
        'info': info,
        'error': error,
        'paginator': paginated_games,
        'page_obj': {
            'items': sliced_games,
            'number': paginated_games.page,
            'has_other_pages': True if len(paginated_games.pages) > 1 else False,
            'has_previous': paginated_games.has_prev,
            'has_next': paginated_games.has_next,
            'paginator': {'page_range': paginated_games.pages},
            'previous_page_number': paginated_games.page-1,
            'next_page_number': paginated_games.page+1,
        },
        'size': paginated_games.per_page,
        'form': form,
    }
    return render_template('shop_page.html', **context)


@app.route('/purchased_applications/')
def users_game_page():
    global curr_user

    # technical variables
    games = []
    error = {}
    if curr_user:
        curr_user = db.session.get(Buyer, curr_user.id)
        games = curr_user.buyers_game

    else:
        error.update({'error': 'Вы не авторизованы. Пожалуйста, войдите в аккаунт или зарегистрируйтесь.'})

    # variables for paginate
    size = 5
    page = 1 if request.args.get('page') is None else int(request.args.get('page'))
    sliced_games = games[page * size - size:page * size]
    paginated_games = Pagination(total=len(games), per_page=size, page=page)
    if len(paginated_games.pages) < page:
        sliced_games = games[len(paginated_games.pages) * size - size:len(paginated_games.pages) * size]
        paginated_games = Pagination(total=len(games), per_page=size, page=len(paginated_games.pages))

    context = {
        'user': curr_user,
        'error': error,
        'paginator': paginated_games,
        'page_obj': {
            'items': sliced_games,
            'number': paginated_games.page,
            'has_other_pages': True if len(paginated_games.pages) > 1 else False,
            'has_previous': paginated_games.has_prev,
            'has_next': paginated_games.has_next,
            'paginator': {'page_range': paginated_games.pages},
            'previous_page_number': paginated_games.page-1,
            'next_page_number': paginated_games.page+1,
        },
        'size': paginated_games.per_page,
    }
    return render_template('users_game_page.html', **context)


if __name__ == '__main__':
    app.run()
