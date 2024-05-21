from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView
from django_filters import FilterSet, RangeFilter, DateRangeFilter, DateFilter, ChoiceFilter
from django_filters.views import FilterView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from .forms import ProfileForm
from django.shortcuts import render, redirect
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
    
def generate_qr_code(request):
    data = "Profile"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # บันทึกภาพ QR code เป็นไฟล์
    img_path = "media/qr_codes/qr_code.png"
    img.save(img_path)

    # ส่งภาพ QR code กลับเป็น HttpResponse
    with open(img_path, "rb") as f:
        response = HttpResponse(f.read(), content_type="image/png")
        response["Content-Disposition"] = "attachment; filename=qr_code.png"
    return response
    pass

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

def checkin_users(request):
    if request.method == 'POST':
        room = request.POST.get('room')
        degree = request.POST.get('degree')
        department = request.POST.get('department')
        presence = int(request.POST.get('presence'))  # 0 for Absent, 1 for Present

        # ตรวจสอบว่ามีข้อมูลที่ถูกส่งมาหรือไม่
        if room and degree and department:
            # สร้างเงื่อนไขการกรองผู้ใช้
            user_filter = {
                'room': room,
                'degree': degree,
                'department': department
            }

            # กรองผู้ใช้ตามเงื่อนไข
            filtered_users = Profile.objects.filter(**user_filter)

            # ตรวจสอบว่ามีผู้ใช้ที่ตรงกับเงื่อนไขหรือไม่
            if filtered_users.exists():
                # สร้างการเช็คชื่อสำหรับผู้ใช้ที่ผ่านการกรองแล้ว
                checkins_to_create = []
                for user in filtered_users:
                    checkins_to_create.append(AttendanceCheckin(
                        user=user,
                        room=room,
                        degree=degree,
                        department=department,
                        presence=presence
                    ))

                # บันทึกการเช็คชื่อลงในฐานข้อมูล
                AttendanceCheckin.objects.bulk_create(checkins_to_create)

                return JsonResponse({'message': 'Checkin successful!'})
            else:
                return JsonResponse({'message': 'No users found matching the criteria'}, status=400)
        else:
            return JsonResponse({'message': 'Missing room, degree, or department'}, status=400)
    else:
        return JsonResponse({'message': 'Invalid request method!'}, status=400)

