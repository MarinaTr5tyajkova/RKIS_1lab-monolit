from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
import re


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'Email обязателен для заполнения.',
            'invalid': 'Введите корректный email адрес.'
        }
    )

    full_name = forms.CharField(
        label='ФИО',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'ФИО обязательно для заполнения.'
        }
    )

    username = forms.CharField(
        label='Логин',
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'Логин обязателен для заполнения.'
        }
    )

    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True
    )

    password2 = forms.CharField(
        label='Повтор пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True
    )

    consent = forms.BooleanField(
        label='Согласие на обработку персональных данных',
        required=True,
        error_messages={
            'required': 'Необходимо согласие на обработку персональных данных.'
        }
    )

    avatar = forms.ImageField(required=True)  # Добавлено поле для загрузки аватара

    class Meta:
        model = User
        fields = ['full_name', 'username', 'email', 'password1', 'password2', 'consent', 'avatar']

    def clean_full_name(self):
        full_name = self.cleaned_data['full_name']
        if not re.match(r'^[А-Яа-яЁё\s\-]+$', full_name):
            raise ValidationError('ФИО должно содержать только кириллические буквы, пробелы и дефисы.')
        return full_name

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.match(r'^[a-zA-Z0-9\-]+$', username):
            raise ValidationError('Логин должен содержать только латиницу, цифры и дефисы.')

        if User.objects.filter(username=username).exists():
            raise ValidationError('Этот логин уже занят.')

        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Пароли не совпадают.")

    def save(self, commit=True):
        user = super().save(commit)

        # Создание профиля пользователя с загруженным аватаром
        UserProfile.objects.create(user=user, avatar=self.cleaned_data['avatar'])

        return user

class LoginForm(forms.Form):
    username = forms.CharField(required=True, max_length=200, label='', widget=forms.TextInput(attrs={'placeholder': 'Имя пользователя'}))
    password = forms.CharField(required=True, max_length=200, label='', widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}))

class UserProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    full_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio']  # Добавьте другие поля из модели UserProfile по мере необходимости

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].widget.attrs.update({'class': 'form-control-file'})

