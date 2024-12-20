import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', default='default_avatar.png')
    bio = models.TextField(blank=True)
    full_name = models.CharField(max_length=100, blank=True)  # Поле для ФИО

    def __str__(self):
        return self.user.username

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    image = models.ImageField(upload_to='questions/', blank=True, null=True)  # Поле для изображения

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

    def __str__(self):
        return self.question_text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')  # Связь с вопросом
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Ссылка на пользовательскую модель
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    def __str__(self):
        return self.title  # Возвращает заголовок при печати или отображении объекта

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Пользователь, который проголосовал
    question = models.ForeignKey(Question, on_delete=models.CASCADE)  # Вопрос, за который проголосовали

    class Meta:
        unique_together = ('user', 'question')  # Уникальная пара (пользователь, вопрос)

    def __str__(self):
        return f"{self.user.username} voted on {self.question.question_text}"