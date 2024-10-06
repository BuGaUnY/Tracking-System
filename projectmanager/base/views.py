from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView
from django_filters import FilterSet, RangeFilter, DateRangeFilter, DateFilter, ChoiceFilter
from django_filters.views import FilterView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from .forms import ProfileForm
from django.shortcuts import render, get_object_or_404, redirect
from .models import Profile
import django_filters
import qrcode
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from activity.models import AttendanceCheckin
# Create your views here.

class ProfileDetail(LoginRequiredMixin, TemplateView):
    template_name = 'base/profile-detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = Profile.objects.get(user=self.request.user)
        return context

class ProfielUpdate(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Profile
    template_name = 'base/profile-update.html'
    form_class = ProfileForm
    success_message = 'แก้ไขโปรไฟล์เรียบร้อยแล้ว'

    def get_object(self):
        return Profile.objects.get(user=self.request.user)

    def get_success_url(self):
        return reverse('profile-detail')
    
class StudentListView(ListView):
    model = Profile
    template_name = 'base/students.html'

class StudentFilter(django_filters.FilterSet):
    degree = ChoiceFilter(choices=Profile.DEGREE_CHOICES, field_name='degree')
    department = ChoiceFilter(choices=Profile.DEPARTMENT_CHOICES, field_name='department')
    class Meta:
        model = Profile
        fields = ['room', 'degree', 'department']

    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['room'].label = 'ห้อง'
        self.filters['degree'].label = 'ระดับชั้น'
        self.filters['department'].label = 'แผนก'

class StudentSearch(FilterView):
    template_name = 'base/student-search.html'
    filterset_class = StudentFilter


