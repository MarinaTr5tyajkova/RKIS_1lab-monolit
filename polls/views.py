from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.views.generic import ListView, DetailView, UpdateView, View
from .models import UserProfile, Post, Question, Choice
from django.urls import reverse_lazy
from .forms import UserProfileForm, UserRegistrationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils import timezone


# Просмотр списка записей в блоге (список вопросов)
class HomeView(ListView):
    model = Post
    template_name = 'polls/home.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return Post.objects.order_by('-date_posted')  # Упорядочивать публикации по дате публикации


# Регистрация пользователя
class RegisterView(View):
    def get(self, request):
        form = UserRegistrationForm()
        return render(request, 'polls/register.html', {'form': form})

    def post(self, request):
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()  # Сохраняем пользователя

            # Проверяем, существует ли профиль
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            if created:
                user_profile.avatar = form.cleaned_data['avatar']
                user_profile.full_name = form.cleaned_data['full_name']
                user_profile.save()

            return redirect('polls:home')  # Перенаправление после успешной регистрации
        return render(request, 'polls/register.html', {'form': form})


# Редактирование профиля
class EditProfileView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'polls/edit_profile.html'
    success_url = reverse_lazy('polls:home')

    def get_object(self, queryset=None):
        return self.request.user.userprofile

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class QuestionListView(ListView):
    model = Question
    template_name = 'polls/home.html'  # Используем home.html вместо question_list.html
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]  # Получаем последние 5 опубликованных вопросов

# Для отображения подробной информации по конкретному вопросу
class QuestionDetailView(DetailView):
    model = Question
    template_name = 'polls/detail.html'


# Для отображения результатов по конкретному вопросу
class ResultsView(DetailView):
    model = Question
    template_name = 'polls/results.html'


# Класс для голосования по вопросу
class VoteView(LoginRequiredMixin, View):  # Добавляем LoginRequiredMixin для проверки авторизации пользователя
    def post(self, request, question_id):
        question = get_object_or_404(Question, pk=question_id)

        try:
            selected_choice = question.choice_set.get(pk=request.POST['choice'])
        except (KeyError, Choice.DoesNotExist):
            return render(request, 'polls/detail.html', {
                'question': question,
                'error_message': "Вы не сделали выбор.",
            })
        else:
            selected_choice.votes += 1
            selected_choice.save()
            return redirect('polls:results', question.id)


# Удаление профиля пользователя
class DeleteProfileView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = request.user
        user.delete()  # Удаляем пользователя и его профиль
        logout(request)  # Выход из системы после удаления профиля
        return redirect('polls:home')  # Перенаправление на главную страницу


@login_required  # Проверка авторизации для доступа к профилю пользователя
def profile(request):
    user_profile = request.user.userprofile  # Получаем профиль пользователя
    return render(request, 'polls/profile.html', {
        'user': request.user,
        'user_profile': user_profile,
    })