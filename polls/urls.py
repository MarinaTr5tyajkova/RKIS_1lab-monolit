from django.urls import path
from .views import HomeView, RegisterView, EditProfileView, DeleteProfileView, QuestionListView, QuestionDetailView, \
    ResultsView, VoteView, profile, CreateQuestionView
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'polls'

urlpatterns = [
    path('', QuestionListView.as_view(), name='home'),  # Главная страница с постами
    path('register/', RegisterView.as_view(), name='register'),  # Страница регистрации
    path('edit-profile/', EditProfileView.as_view(), name='edit_profile'),  # Страница редактирования профиля
    # path('questions/', QuestionListView.as_view(), name='question_list'),  # Список вопросов
    path('create/', CreateQuestionView.as_view(), name='create_question'),
    path('questions/<int:pk>/', QuestionDetailView.as_view(), name='detail'),  # Подробная информация по вопросу
    path('questions/<int:pk>/results/', ResultsView.as_view(), name='results'),  # Результаты голосования по вопросу
    path('questions/<int:question_id>/vote/', VoteView.as_view(), name='vote'),  # Голосование по вопросу
    path('login/', auth_views.LoginView.as_view(template_name='polls/login.html'), name='login'),  # Страница входа
    path('logout/', auth_views.LogoutView.as_view(next_page='polls:home'), name='logout'),  # Выход из системы
    path('delete-profile/', DeleteProfileView.as_view(), name='delete_profile'),  # Удаление профиля
    path('profile/', profile, name='profile'),  # Страница профиля пользователя
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Обработка медиафайлов