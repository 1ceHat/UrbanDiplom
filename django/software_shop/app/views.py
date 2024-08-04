from django.shortcuts import render
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
    info = {}
    size = request.GET.get('size', 3)
    games = Game.objects.all()
    page_num = request.GET.get('page')

    paginator = Paginator(games, per_page=size)
    page_obj = paginator.get_page(page_num)

    #paginator.num

    if request.method == 'POST':
        global user_id
        game_id = request.POST.get('game_to_buy')
        game = Game.objects.get(id=game_id)
        if user_id:
            if user_id.balance < game.cost:
                info.update({
                    'error': 'Недостаточно средств'
                })
            elif game.buyer.filter(id=user_id.id).exists():
                info.update({
                    'error': 'У вас уже куплена эта игра'
                })
            elif game.age_limited and user_id.age < 18:
                info.update({
                    'error': 'Вам не доступна эта игра'
                })
            else:
                game.buyer.set((user_id,))
                user_id.balance -= game.cost
                info.update({
                    'message': f'{game.title} куплена!'
                })

        else:
            info.update({
                'error': 'Вы не авторизованы. Пожалуйста, войдите в аккаунт.'
            })

    context = {
        'games': games,
        'page_obj': page_obj,
        'size': size,
        'p_games': paginator,
        'info': info,
        'user': user_id,
    }
    return render(request, 'shop_page.html', context=context)


def users_game_page(request):
    global user_id
    info = {}
    users_game = None
    if user_id is None:
        info.update({
            'error': 'Войдите в аккаунт, чтобы просмотреть ваши покупки',
            'login': ' Войти'
        })
    else:
        users_game = Game.objects.filter(buyer=user_id)

    context = {
        'error': info,
        'application': users_game,
        'user': user_id,
    }
    return render(request, 'users_game_page.html', context)


def log_in(request):
    users = Buyer.objects.all()
    info = {}
    if request.method == 'POST':
        form = UserAuthorise(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            if not users.filter(name=username).exists():
                info.update({
                    'error': 'Такого пользователя не существует',
                    'message': 'У вас ещё нет аккаунта?',
                    'signup': 'Зарегистрируйтесь!!'
                })
            elif password != users.get(name=username).password:
                info.update({'error': 'Неверный пароль'})
            else:
                info.update({'message': f'Приветствуем, {username}!'})
                global user_id
                user_id = users.get(name=username)
                return render(request, 'main_page.html', context={'info': info})
    else:
        form = UserRegister()
    info.update({'form': form})
    return render(request, 'login_page.html', context={'info': info})


def sign_up(request):
    users = Buyer.objects.all()
    info = {}
    if request.method == 'POST':
        form = UserRegister(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            repeat_password = form.cleaned_data['repeat_password']
            age = form.cleaned_data['age']

            if users.filter(name=username).exists():
                info.update({
                    'error': 'Пользователь с таким именем существует',
                    'message': 'У вас уже есть аккаунт?',
                    'login': 'Войдите!'
                })
            elif password != repeat_password:
                info.update({'error': 'Пароли не совпадают'})
            else:
                info.update({'message': f'Приветствуем, {username}!'})
                global user_id
                user_id = Buyer.objects.create(name=username, password=password, age=age)
                return render(request, 'main_page.html', context={'info': info})
    else:
        form = UserRegister()
    info.update({'form': form})
    return render(request, 'registration_page.html', context={'info': info})