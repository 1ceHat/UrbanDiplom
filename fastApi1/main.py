import uvicorn
from fastapi import FastAPI, HTTPException, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_pagination import add_pagination, paginate, Params

from app.database import *
from sqlalchemy import select, insert, update
from sqlalchemy.orm import Session

from typing import Annotated
from fastapi.templating import Jinja2Templates

app = FastAPI()
add_pagination(app)
templates = Jinja2Templates(directory='app/templates')
curr_user = None


@app.get('/')
async def main_page(request: Request) -> HTMLResponse:
    global curr_user
    info = {}
    context = {
        'request': request,
        'info': info,
        'user': curr_user,
    }
    return templates.TemplateResponse('main_page.html', context=context)


@app.get('/registration')
async def get_signup_page(request: Request) -> HTMLResponse:
    context = {
        'request': request,
        'user': curr_user,
        'info': {},
    }
    return templates.TemplateResponse('registration_page.html', context=context)


@app.post('/registration')
async def post_signup_page(request: Request,
                           username: Annotated[str, Form()],
                           password: Annotated[str, Form()],
                           repeat_password: Annotated[str, Form()],
                           age: Annotated[int, Form()],
                           db: Annotated[Session, Depends(get_db)]):
    global curr_user
    check_user = db.scalars(select(Buyer).where(Buyer.name == username)).first()
    info = {}
    if curr_user is None:
        if check_user is not None:
            info.update({'error': 'Пользователь с таким именем существует',
                         'message': 'У вас уже есть аккаунт?',
                         'login': 'Авторизуйтесь!'})
        elif password != repeat_password:
            info.update({'error': 'Пароли не совпадают'})
        else:
            db.execute(insert(Buyer).values(name=username,
                                            password=password,
                                            age=age))
            db.commit()
            curr_user = check_user
            return RedirectResponse('/', status_code=302)

    context = {
        'request': request,
        'info': info,
        'user': curr_user,
    }
    return templates.TemplateResponse('registration_page.html', context=context)


@app.get('/login')
async def get_login_page(request: Request) -> HTMLResponse:
    context = {
        'request': request,
        'user': curr_user,
        'info': {},
    }
    return templates.TemplateResponse('login_page.html', context=context)


@app.post('/login')
async def post_login_page(request: Request,
                          username: Annotated[str, Form()],
                          password: Annotated[str, Form()],
                          db: Annotated[Session, Depends(get_db)]):
    global curr_user
    info = {}
    if curr_user is None:
        check_user = db.scalars(select(Buyer).where(Buyer.name == username)).first()
        if check_user is None:
            info.update({'error': 'Такого пользователя не существует',
                         'message': 'У вас ещё нет аккаунта?',
                         'signup': 'Зарегистрируйтесь!'})
        elif check_user.password != password:
            info.update({'error': 'Неверный пароль'})
        else:
            curr_user = check_user
            return RedirectResponse('/', status_code=302)

    context = {
        'request': request,
        'info': info,
        'user': curr_user,
    }
    return templates.TemplateResponse('login_page.html', context=context)


@app.get('/purchased_applications')
async def get_purchased_applications(request: Request, db: Annotated[Session, Depends(get_db)]) -> HTMLResponse:
    global curr_user
    applications = []
    if curr_user:
        curr_user = db.get(Buyer, curr_user.id)
        applications = curr_user.buyers_game
    context = {
        'request': request,
        'user': curr_user,
        'applications': applications,
    }
    return templates.TemplateResponse('users_game_page.html', context=context)


@app.get('/shop')
async def get_shop_page(request: Request,
                        db: Annotated[Session, Depends(get_db)],
                        page: int = 1, size: int = 3) -> HTMLResponse:
    global curr_user
    games = db.scalars(select(Game)).all()
    params = Params(size=int(size), page=page)
    paginated_games = paginate(games, params)
    context = {
        'request': request,
        'user': curr_user,
        'games': paginated_games,
        'size': size,
        'info': {},
    }
    return templates.TemplateResponse('shop_page.html', context=context)


@app.post('/shop')
async def post_shop_page(request: Request,
                         db: Annotated[Session, Depends(get_db)],
                         game_title: Annotated[str, Form()],
                         size: Annotated[int, Form()], page: Annotated[int, Form()]) -> HTMLResponse:
    global curr_user
    game = db.scalars(select(Game).where(Game.title == game_title)).first()
    games = db.scalars(select(Game)).all()
    info = {}
    params = Params(size=int(size), page=page)
    paginated_games = paginate(games, params)
    if not curr_user:
        info.update({'error': 'Войдите в аккаунт или зарегистрируйтесь!'})
    else:
        curr_user = db.get(Buyer, curr_user.id)
        if curr_user.balance < game.cost:
            info.update({'error': 'Недостаточно средств'})
        elif game.age_limited and curr_user.age < 18:
            info.update({'error': 'Вы не достигли возраста покупки'})
        elif game in curr_user.buyers_game:
            info.update({'error': 'У Вас уже куплена эта игра'})
        else:
            curr_user.balance -= game.cost
            curr_user.buyers_game.append(game)
            db.commit()

    context = {
        'request': request,
        'user': curr_user,
        'games': paginated_games,
        'size': size,
        'info': info,
    }
    return templates.TemplateResponse('shop_page.html', context=context)


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
