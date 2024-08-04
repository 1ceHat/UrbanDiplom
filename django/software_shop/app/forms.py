from django import forms


class UserRegister(forms.Form):
    username = forms.CharField(min_length=3, max_length=30, label='Введите логин')
    password = forms.CharField(min_length=8, label='Введите пароль')
    repeat_password = forms.CharField(min_length=8, label='Повторите пароль')
    age = forms.IntegerField(max_value=120, label='Введите возраст')


class UserAuthorise(forms.Form):
    username = forms.CharField(max_length=30, label='Введите логин', required=True)
    password = forms.CharField(max_length=30, label='Введите пароль', required=True)