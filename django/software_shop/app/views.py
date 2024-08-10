from django.shortcuts import render, redirect
from .forms import *
from django.core.paginator import Paginator
from .models import *

# Create your views here.
user_id = None


def main_page(request):
    global user_id
    context = {
        'user': user_id
    }
    return render(request, 'main_page.html', context=context)


def shop_page(request):
    global user_id
    info = {}
    error = {}
    size = request.GET.get('size', 3)
    games = Game.objects.all()
    page_num = request.GET.get('page')

    paginator = Paginator(games, per_page=size)
    page_obj = paginator.get_page(page_num)

    if request.method == 'POST':
        game_id = request.POST.get('game_to_buy')
        game = Game.objects.get(id=game_id)
        if user_id:
            if user_id.balance < game.cost:
                error.update({
                    'error': 'Недостаточно средств'
                })
            elif game.buyer.filter(id=user_id.id).exists():
                error.update({
                    'error': 'У вас уже куплена эта игра'
                })
            elif game.age_limited and user_id.age < 18:
                error.update({
                    'error': 'Вам не доступна эта игра'
                })
            else:
                game.buyer.set((user_id,))
                user_id.balance -= game.cost
                info.update({
                    'message': f'{game.title} куплена!'
                })

        else:
            error.update({
                'error': 'Вы не авторизованы. Пожалуйста, войдите в аккаунт или зарегистрируйтесь.'
            })

    context = {
        'games': games,
        'page_obj': page_obj,
        'size': size,
        'p_games': paginator,
        'info': info,
        'error': error,
        'user': user_id,
        'paginator': paginator,
    }
    return render(request, 'shop_page.html', context=context)


def users_game_page(request):
    global user_id
    error = {}
    users_game = None
    page_num = request.GET.get('page', 1)
    paginator = None
    page_obj = None
    if user_id:
        users_game = Game.objects.filter(buyer=user_id)
        paginator = Paginator(users_game, per_page=5)
        page_obj = paginator.get_page(page_num)
    else:
        error.update({
            'error': 'Вы не авторизованы. Пожалуйста, войдите в аккаунт или зарегистрируйтесь.'
        })

    context = {
        'application': users_game,
        'paginator': paginator,
        'page_obj': page_obj,
        'user': user_id,
        'error': error,
    }
    return render(request, 'users_game_page.html', context)


def log_in(request):
    users = Buyer.objects.all()
    info = {}
    error = {}
    if request.method == 'POST':
        form = UserAuthorise(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            if not users.filter(name=username).exists():
                error.update({
                    'error': 'Такого пользователя не существует',
                    'message': 'У вас ещё нет аккаунта?',
                    'signup': 'Зарегистрируйтесь!!'
                })
            elif password != users.get(name=username).password:
                error.update({'error': 'Неверный пароль'})
            else:
                global user_id
                user_id = users.get(name=username)
                return redirect('/')
    else:
        form = UserRegister()
    info.update({'form': form})
    context = {'info': info,
               'error': error,}
    return render(request, 'login_page.html', context=context)


def sign_up(request):
    users = Buyer.objects.all()
    info = {}
    error = {}
    if request.method == 'POST':
        form = UserRegister(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            repeat_password = form.cleaned_data['repeat_password']
            age = form.cleaned_data['age']

            if users.filter(name=username).exists():
                error.update({
                    'error': 'Пользователь с таким именем существует',
                })
            elif password != repeat_password:
                error.update({'error': 'Пароли не совпадают'})
            else:
                global user_id
                user_id = Buyer.objects.create(name=username, password=password, age=age)
                return redirect('/')
    else:
        form = UserRegister()
    info.update({'form': form})
    context = {'info': info,
               'error': error,}
    return render(request, 'registration_page.html', context=context)
