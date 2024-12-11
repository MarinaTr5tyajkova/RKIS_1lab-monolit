from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Question, Choice
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
import re

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'image']

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text']

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

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise ValidationError("Электронная почта уже используется.")
        return email

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
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
            # Создаем или обновляем профиль пользователя
            user_profile = UserProfile.objects.create(
                user=user,
                avatar=self.cleaned_data['avatar'],
                full_name=self.cleaned_data['full_name'],
            )

        return user

        return user

class LoginForm(forms.Form):
    username = forms.CharField(required=True, max_length=200, label='', widget=forms.TextInput(attrs={'placeholder': 'Имя пользователя'}))
    password = forms.CharField(required=True, max_length=200, label='', widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}))

class UserProfileForm(forms.ModelForm):
    full_name = forms.CharField(required=True, label='Полное имя', widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'full_name']  # Уберите email из полей формы

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].widget.attrs.update({'class': 'form-control-file'})
        self.fields['bio'].widget.attrs.update({'class': 'form-control', 'rows': 3})
        self.fields['full_name'].widget.attrs.update({'class': 'form-control'})
