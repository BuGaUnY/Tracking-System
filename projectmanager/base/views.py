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

class StudentFilter(FilterSet):
    room = django_filters.CharFilter(field_name='room', lookup_expr='icontains')  # เพิ่มการค้นหาแบบไม่สนใจตัวพิมพ์ใหญ่
    department = ChoiceFilter(choices=Profile.DEPARTMENT_CHOICES, field_name='department')

    class Meta:
        model = Profile
        fields = ['room', 'department']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['room'].label = 'ห้อง'
        self.filters['department'].label = 'แผนก'

class StudentSearchView(FilterView, ListView):
    model = Profile
    template_name = 'base/student-search.html'  # เปลี่ยนชื่อตามที่คุณใช้
    filterset_class = StudentFilter
    context_object_name = 'object_list'  # ใช้สำหรับการอ้างอิงใน template

    def get_queryset(self):
        # เริ่มต้นด้วยการดึงโปรไฟล์ทั้งหมด โดยกรองค่า room และ department ที่เป็น None หรือว่าง
        queryset = Profile.objects.exclude(room__isnull=True, room='').exclude(department__isnull=True, department='')

        # ตรวจสอบการกรองจากฟิลด์ room และ department
        if self.request.GET.get('room'):
            queryset = queryset.filter(room=self.request.GET.get('room'))

        if self.request.GET.get('department'):
            queryset = queryset.filter(department=self.request.GET.get('department'))

        return queryset.order_by('student_number')  # เรียงตาม student_number


