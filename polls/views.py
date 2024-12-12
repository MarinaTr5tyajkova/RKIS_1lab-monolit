from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.views.generic import ListView, DetailView, UpdateView, View
from .models import UserProfile, Post, Question, Choice, Vote
from django.urls import reverse_lazy
from .forms import UserProfileForm, UserRegistrationForm, QuestionForm, ChoiceForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils import timezone


# Просмотр списка записей в блоге (список вопросов)
class HomeView(ListView):
    model = Post  # Модель для отображения списка постов
    template_name = 'polls/home.html'  # Шаблон для отображения списка постов
    context_object_name = 'posts'  # Имя контекста для передачи в шаблон

    def get_queryset(self):
        return Post.objects.order_by('-date_posted')  # Упорядочивает публикации по дате публикации (новые первыми)


# Регистрация пользователя
class RegisterView(View):
    def get(self, request):
        form = UserRegistrationForm()  # Создаем пустую форму регистрации
        return render(request, 'polls/register.html', {'form': form})  # Отображаем страницу регистрации с формой

    def post(self, request):
        form = UserRegistrationForm(request.POST, request.FILES)  # Создаем форму с данными из POST-запроса
        if form.is_valid():  # Проверяем валидность формы
            user = form.save()  # Сохраняем пользователя

            # Проверяем, существует ли профиль
            user_profile, created = UserProfile.objects.get_or_create(
                user=user)  # Создаем профиль пользователя или получаем существующий
            if created:  # Если профиль был создан только что
                user_profile.avatar = form.cleaned_data['avatar']  # Устанавливаем аватар из формы
                user_profile.full_name = form.cleaned_data['full_name']  # Устанавливаем полное имя из формы
                user_profile.save()  # Сохраняем профиль

            return redirect('polls:home')  # Перенаправляем на главную страницу после успешной регистрации
        return render(request, 'polls/register.html', {'form': form})  # Если форма не валидна, отображаем её снова


# Редактирование профиля
class EditProfileView(LoginRequiredMixin, UpdateView):
    model = UserProfile  # Модель профиля пользователя для редактирования
    form_class = UserProfileForm  # Форма для редактирования профиля
    template_name = 'polls/edit_profile.html'  # Шаблон для редактирования профиля
    success_url = reverse_lazy('polls:home')  # URL для перенаправления после успешного сохранения

    def get_object(self, queryset=None):
        return self.request.user.userprofile  # Получаем профиль текущего пользователя

    def form_valid(self, form):
        user_profile = form.save(commit=False)  # Сохраняем профиль без немедленного сохранения в БД
        user_profile.save()  # Сохраняем профиль в БД

        email = self.request.POST.get('email')  # Получаем email из POST-запроса
        user = self.request.user  # Получаем текущего пользователя
        user.email = email  # Обновляем email пользователя
        user.save()  # Сохраняем изменения в модели пользователя

        return super().form_valid(form)  # Возвращаем результат обработки формы


# Класс для отображения списка вопросов
class QuestionListView(ListView):
    model = Question  # Модель вопросов для отображения списка
    template_name = 'polls/home.html'  # Используем тот же шаблон home.html вместо question_list.html
    context_object_name = 'latest_question_list'  # Имя контекста для передачи в шаблон

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]
        # Получаем последние 5 опубликованных вопросов (дата публикации меньше или равна текущему времени)


# Для отображения подробной информации по конкретному вопросу
class QuestionDetailView(DetailView):
    model = Question  # Модель вопросов для отображения деталей вопроса
    template_name = 'polls/detail.html'  # Шаблон для отображения деталей вопроса


# Для отображения результатов по конкретному вопросу
class ResultsView(DetailView):
    model = Question  # Модель вопросов для отображения результатов голосования
    template_name = 'polls/results.html'  # Шаблон для отображения результатов голосования


# Класс для голосования по вопросу
class VoteView(LoginRequiredMixin, View):
    def post(self, request, question_id):
        question = get_object_or_404(Question, pk=question_id)
        # Получаем вопрос по его ID или возвращаем ошибку 404 если не найден

        if Vote.objects.filter(user=request.user, question=question).exists():
            return render(request, 'polls/detail.html', {
                'question': question,
                'error_message': "Вы уже проголосовали за этот опрос.",
                # Если пользователь уже голосовал за этот вопрос, показываем сообщение об ошибке.
            })

        try:
            selected_choice = question.choices.get(pk=request.POST['choice'])
            # Получаем выбранный вариант ответа по его ID из POST-запроса.
        except (KeyError, Choice.DoesNotExist):
            return render(request, 'polls/detail.html', {
                'question': question,
                'error_message': "Вы не сделали выбор.",
                # Если выбор не был сделан или вариант не существует.
            })
        else:
            selected_choice.votes += 1
            selected_choice.save()
            # Увеличиваем количество голосов за выбранный вариант и сохраняем изменения.

            Vote.objects.create(user=request.user, question=question)
            # Сохраняем информацию о голосе.

            return redirect('polls:results', question.id)
            # Перенаправляем на страницу результатов голосования.


# Удаление профиля пользователя
class DeleteProfileView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = request.user
        user.delete()
        # Удаляем пользователя и его профиль.

        logout(request)
        # Выход из системы после удаления профиля.

        return redirect('polls:home')
        # Перенаправление на главную страницу после удаления профиля.


@login_required
def profile(request):
    user_profile = request.user.userprofile
    # Получаем профиль текущего пользователя.

    return render(request, 'polls/profile.html', {
        'user': request.user,
        'user_profile': user_profile,
        # Передаем информацию о пользователе и его профиле в шаблон.
    })


class CreateQuestionView(View):
    def get(self, request):
        question_form = QuestionForm()
        return render(request, 'polls/create_question.html', {
            'question_form': question_form,
            # Отображаем форму создания нового вопроса.
        })

    def post(self, request):
        question_form = QuestionForm(request.POST, request.FILES)

        if question_form.is_valid():
            question = question_form.save()
            # Сохраняем новый вопрос.

            choice_texts = request.POST.getlist('choice_text')
            # Получаем варианты ответов из формы.

            for text in choice_texts:
                if text:
                    Choice.objects.create(question=question, choice_text=text)
                    # Создаем варианты ответов только если текст не пустой.

            return redirect('polls:home')
            # Перенаправляем на главную страницу после успешного создания вопроса.

        return render(request, 'polls/create_question.html', {
            'question_form': question_form,
            # Если форма не валидна, отображаем её снова с ошибками.
        })
