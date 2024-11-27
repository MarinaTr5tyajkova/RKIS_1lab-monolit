from django.urls import path
from .views import HomeView, RegisterView, EditProfileView, DeleteProfileView, DetailView, ResultsView, vote
from django.contrib.auth import views as auth_views
from .views import profile
from django.conf.urls.static import static
from django.conf import settings

app_name = 'polls'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),  # Corrected this line
    path('register/', RegisterView.as_view(), name ='register'),
    path('edit_profile/', EditProfileView.as_view(), name='edit_profile'),
    path('<int:pk>/', DetailView.as_view(), name='detail'),  # Same here for DetailView
    path('<int:pk>/results/', ResultsView.as_view(), name='results'),  # Same here for ResultsView
    path('<int:question_id>/vote/', vote, name='vote'),  # Same here for vote function
    path('login/', auth_views.LoginView.as_view(template_name='polls/login.html'), name='login'),  # Login view
    path('logout/', auth_views.LogoutView.as_view(next_page='polls:home'), name='logout'),  # Logout view
    path('delete_profile/', DeleteProfileView.as_view(), name='delete_profile'),
    path('profile/', profile, name='profile'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)