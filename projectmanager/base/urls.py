from django.urls import path
from . import views
from .views import StudentSearchView

urlpatterns = [
    path('profile/', views.ProfileDetail.as_view(), name='profile-detail'),
    path('profile/update/', views.ProfielUpdate.as_view(), name='profile-update'),
    path('students/search/', views.StudentSearchView.as_view(), name='student-search'),
]