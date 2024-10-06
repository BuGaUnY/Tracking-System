from django.urls import path
from . import views
from .views import StudentListView, StudentSearch

urlpatterns = [
    path('profile/', views.ProfileDetail.as_view(), name='profile-detail'),
    path('profile/update/', views.ProfielUpdate.as_view(), name='profile-update'),
    path('students/', StudentListView.as_view(), name='students'),
    path('students/search/', views.StudentSearch.as_view(), name='student-search'),
]