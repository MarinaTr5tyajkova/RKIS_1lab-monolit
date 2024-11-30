from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView, UpdateView, ListView
from django.views import View
from .models import UserProfile, Post, Question, Choice
from django.urls import reverse_lazy
from django.views import generic
from .forms import UserProfileForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required


# Просмотр списка записей в блоге (список вопросов)
class HomeView(ListView):
    model = Post
    template_name = 'polls/home.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return Post.objects.order_by('-date_posted') # Упорядочивать публикации по дате публикации

# Регистрация пользователя
class RegisterView(View):
    def get(self, request):
        form = UserRegistrationForm()
        return render(request, 'polls/register.html', {'form': form})

    def post(self, request):
        form = UserRegistrationForm(request.POST, request.FILES)  # Не забудьте передать request.FILES
        if form.is_valid():
            form.save()  # Сохранение как пользователя, так и профиля с аватаром
            return redirect('polls:home')  # Перенаправление после успешной регистрации
        return render(request, 'polls/register.html', {'form': form})

# Редактирование профиля
class EditProfileView(LoginRequiredMixin, UpdateView) :
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'polls/edit_profile.html'
    success_url = reverse_lazy('polls:home')

    def get_object(self, queryset = None):
        return self.request.user.userprofile

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

# Для отображения подробной информации по конкретному вопросу
class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

# Для отображения результатов по конкретному вопросу
class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

# Функция для обработки голосования по вопросу
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    # Проверка, проголосовал ли пользоваьель уже
    if request.user in question.voters.all():
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': 'Вы уже проголосовали за этот вопрос.'
        })

    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': 'Вы не сделали выбор'
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        question.voters.add(request.user)
        return redirect('polls:results', question.id)

class DeleteProfileView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = request.user
        user.delete()  # Удаляем пользователя и его профиль
        logout(request)  # Выход из системы после удаления профиля
        return redirect('polls:home')  # Перенаправление на главную страницу

@login_required
def profile(request):
    user_profile = request.user.userprofile  # Получаем профиль пользователя
    return render(request, 'polls/profile.html', {
        'user': request.user,
        'user_profile': user_profile,
    })

@login_required
def delete_profile(request):
    user = request.user
    user.delete()  # Удаляет пользователя и его профиль
    return redirect('home')  # Перенаправление на главную страницу или другую страницу после удаления.

@login_required
def edit_profile(request):
    user = request.user
    profile = user.userprofile
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserRegistrationForm(request.POST, instance=user)  # Создаем форму для обновления пользователя
        if form.is_valid() and user_form.is_valid():
            user_form.save()  # Сохраняем изменения в модели User
            form.save()  # Сохраняем изменения в модели UserProfile
            return redirect('polls:profile')  # Перенаправление на страницу профиля после сохранения
    else:
        form = UserProfileForm(instance=profile)
        user_form = UserRegistrationForm(instance=user)  # Заполняем форму данными пользователя

    return render(request, 'polls/edit_profile.html', {'form': form, 'user_form': user_form})