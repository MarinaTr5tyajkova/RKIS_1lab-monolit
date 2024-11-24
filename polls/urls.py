from django.urls import path
from .views import HomeView, RegisterView, EditProfileView, DetailView, ResultsView, vote

# app_name = 'polls'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),  # Corrected this line
    path('register/', RegisterView.as_view(), name ='register'),
    path('edit_profile/', EditProfileView.as_view(), name='edit_profile'),
    path('<int:pk>/', DetailView.as_view(), name='detail'),  # Same here for DetailView
    path('<int:pk>/results/', ResultsView.as_view(), name='results'),  # Same here for ResultsView
    path('<int:question_id>/vote/', vote, name='vote'),  # Same here for vote function
]