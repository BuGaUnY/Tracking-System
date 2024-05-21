from django.urls import path
from . import views
from .views import generate_qr_code, StudentListView, StudentSearch

urlpatterns = [
    path('profile/', views.ProfileDetail.as_view(), name='profile-detail'),
    path('profile/update/', views.ProfielUpdate.as_view(), name='profile-update'),
    path('generate_qr_code/', generate_qr_code, name='generate_qr_code'),
    path('students/', StudentListView.as_view(), name='students'),
    path('students/search/', views.StudentSearch.as_view(), name='student-search'),
    path('students/attendance/', views.checkin_users, name='attendance'),
]