from django.shortcuts import render, redirect, get_object_or_404
from django.utils.dateparse import parse_date
from django.db.models import Count, Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView
from .models import Activity, Organizer, Ticket , Attendance, AttendanceCheckin
from base.models import Profile
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from .forms import TicketForm, AttendanceCheckinForm, AttendanceCheckinFormSet, CheckinForm
from django.urls import reverse
from django_filters.views import FilterView
from django_filters import FilterSet, RangeFilter, DateRangeFilter, DateFilter, ChoiceFilter
import django_filters
from django import forms
from datetime import datetime
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.utils import timezone
import csv
from django.forms.models import modelformset_factory
from django.core.exceptions import ValidationError, ObjectDoesNotExist

org_pk = 123
ev_pk = 456

# Create your views here.
class OrganizerList(ListView):
    model = Organizer
    template_name = 'activity/organizer-list.html'
    context_object_name = 'organizers'
    ordering = ['-date_create']
class OrganizerDetail(DetailView):
    model = Organizer
    template_name = 'activity/organizer-detail.html'
    context_object_name = 'organizer'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activitys'] = Activity.objects.filter(organizer=self.object)
        return context

class OrganizerOwnerList(LoginRequiredMixin, ListView):
    model = Organizer
    template_name = 'activity/organizer-owner-list.html'
    context_object_name = 'organizers'
    ordering = ['-date_create']

    def get_queryset(self):
        return Organizer.objects.filter(owner=self.request.user.profile)

class OrganizerOwnerDetail(LoginRequiredMixin, DetailView):
    model = Organizer
    template_name = 'activity/organizer-owner-detail.html'
    context_object_name = 'organizer'

    def get_queryset(self):
        return Organizer.objects.filter(owner=self.request.user.profile, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activitys'] = Activity.objects.filter(organizer=self.object)
        return context

org_pk = 123
act_pk = 456
class OrganizerOwnerActivityCheckin(LoginRequiredMixin, TemplateView):
    template_name = 'activity/organizer-owner-activity-checkin.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activity'] = Activity.objects.get(pk=self.kwargs['activity_pk'])
        context['organizer'] = Organizer.objects.get(pk=self.kwargs['organizer_pk'])
        context['org_pk'] = self.kwargs['organizer_pk']
        return context
    
    def post(self, request, *args, **kwargs):
        org_pk = kwargs['organizer_pk']
        act_pk = kwargs['activity_pk']

        url = reverse('organizer-owner-activity-checkin', kwargs={'organizer_pk': org_pk, 'activity_pk': act_pk})
        return redirect(url)

class OrganizerOwnerActivityTicketList(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'activity/organizer-owner-activity-ticket-list.html'
    context_object_name = 'tickets'
    ordering = ['-date_create']

    def get_queryset(self):
        activity = get_object_or_404(Activity, pk=self.kwargs['pk'])
        return Ticket.objects.filter(activity=activity, activity__organizer__owner=self.request.user.profile)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activity'] = get_object_or_404(Activity, pk=self.kwargs['pk'], organizer__owner=self.request.user.profile)
        return context

class CustomDateRangeFilter(DateRangeFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra['choices'][0] = ('today', 'วันนี้')
        self.extra['choices'][1] = ('yesterday', 'เมื่อวานนี้')
        self.extra['choices'][2] = ('week', 'สัปดาห์นี้')
        self.extra['choices'][3] = ('month', 'เดือนนี้')
        self.extra['choices'][4] = ('year', 'ปีนี้')

class ActivityFilter(django_filters.FilterSet):
    date_start = CustomDateRangeFilter()
    class Meta:
        model = Activity
        fields = ['organizer', 'date_start', 'activity_category']

    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['organizer'].label = 'ผู้จัดงาน'
        self.filters['date_start'].label = 'ช่วงเวลาจัดงาน'
        self.filters['activity_category'].label = 'ประเภทงาน'

class ActivitySearch(FilterView):
    template_name = 'activity/activity-search.html'
    filterset_class = ActivityFilter

class ActivityList(ListView):
    model = Activity
    template_name = 'activity/activity-list.html'
    context_object_name = 'activitys'
    paginate_by = 6
    ordering = ['-date_create']

class ActivityDetail(DetailView):
    model = Activity
    template_name = 'activity/activity-detail.html'
    context_object_name = 'activity'

class TicketCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Ticket
    template_name = 'activity/ticket-create.html'
    form_class = TicketForm
    success_message = 'บันทึกข้อมูลเรียบร้อยแล้ว'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activity'] = Activity.objects.get(pk=self.kwargs['pk'])
        return context

    def get_initial(self):
        initial = super().get_initial()
        profile = self.request.user.profile
        initial['first_name'] = profile.first_name
        initial['last_name'] = profile.last_name
        initial['room'] = profile.room
        initial['degree'] = profile.degree
        initial['department'] = profile.department
        return initial

    def form_valid(self, form):
        form.instance.profile = self.request.user.profile
        form.instance.activity = Activity.objects.get(pk=self.kwargs['pk'])
        profile = form.instance.profile
        activity = form.instance.activity
        if Ticket.objects.filter(activity=activity, profile=profile).exists():
            messages.error(self.request, 'คุณได้ลงทะเบียนไปแล้ว')
            return super().form_invalid(form)
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)
    
    def get_success_url(self):
        return reverse('ticket-list')

class TicketList(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'activity/ticket-list.html'
    context_object_name = 'tickets'
    paginate_by = 10
    ordering = ['-date_create']

    def get_queryset(self):
        return Ticket.objects.filter(profile=self.request.user.profile)

class TicketDetail(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = 'activity/ticket-detail.html'
    context_object_name = 'ticket'

    def get_queryset(self):
        ticket = Ticket.objects.filter(profile=self.request.user.profile, pk=self.kwargs['pk'])
        return ticket

class TicketUpdate(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Ticket
    template_name = 'activity/ticket-update.html'
    form_class = TicketForm
    success_message = 'บันทึกข้อมูลเรียบร้อยแล้ว'

    def get_queryset(self):
        ticket = Ticket.objects.filter(profile=self.request.user.profile, pk=self.kwargs['pk'])
        return ticket

    def get_success_url(self):
        return reverse('ticket-detail', kwargs={'pk': self.kwargs['pk']})

def post(self, request, *args, **kwargs):
    if request.htmx:
        activity = Activity.objects.get(uid=request.POST['activity_uid'])
        try:
            ticket = Ticket.objects.get(uid=request.POST['ticket_uid'], activity=activity)
        except Ticket.DoesNotExist:
            ticket = None
        return render(request, 'activity/partials/ticket-checkin.html', {'ticket': ticket})

class TicketCheckin(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if request.htmx:
            activity = Activity.objects.get(uid=request.POST['activity_uid'])
            try:
                ticket = Ticket.objects.get(uid=request.POST['ticket_uid'] , activity = activity)
            except Ticket.DoesNotExist:
                ticket = None
            return render(request, 'activity/partials/ticket-checkin.html', {'ticket': ticket})

class TicketCheckinSuccess(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if request.htmx:
            ticket = get_object_or_404(Ticket, uid=request.POST['ticket_uid'])
            print(ticket)
            ticket.checkin = True
            ticket.save()
            return render(request, 'activity/partials/ticket-detail-partials.html', {'ticket': ticket})

class AttendanceList(ListView):
    model = Attendance
    template_name = 'attendance/attendance_list.html'
    context_object_name = 'attendances'

def bulk_checkin(request, pk):
    attendance = Attendance.objects.get(pk=pk)
    room_filter = request.GET.get('room', None)
    department_filter = request.GET.get('department', None)
    profiles = Profile.objects.all()

    if room_filter:
        profiles = profiles.filter(room=room_filter)

    if department_filter:
        profiles = profiles.filter(department=department_filter)

    AttendanceCheckinFormSet = modelformset_factory(
        AttendanceCheckin,
        form=AttendanceCheckinForm,
        extra=len(profiles)
    )

    date_checkin = timezone.now().date()  # วันที่ปัจจุบัน

    if request.method == 'POST':
        formset = AttendanceCheckinFormSet(request.POST)

        if formset.is_valid():
            instances = formset.save(commit=False)

            for instance in instances:
                instance.att_name = attendance
                instance.date_checkin = date_checkin

                # ตรวจสอบข้อมูลซ้ำในวันนี้โดยใช้ student_number
                exists_by_student = AttendanceCheckin.objects.filter(
                    student_number=instance.student_number,
                    att_name=attendance,
                    date_checkin=date_checkin
                ).exists()

                # ตรวจสอบข้อมูลซ้ำโดยใช้ first_name และ last_name
                exists_by_name = AttendanceCheckin.objects.filter(
                    first_name=instance.first_name,
                    last_name=instance.last_name,
                    att_name=attendance,
                    date_checkin=date_checkin
                ).exists()

                if exists_by_student or exists_by_name:
                    print(f"ข้ามการบันทึกข้อมูลซ้ำสำหรับหมายเลขนักเรียน: {instance.student_number} ในวันที่ {date_checkin}")
                    continue  # ข้ามการบันทึกอินสแตนซ์นี้

                # บันทึกเฉพาะเมื่อไม่มีข้อมูลซ้ำ
                instance.save()

            return redirect('report_list')

    else:
        initial_data = [
            {
                'student_number': profile.student_number,
                'first_name': profile.first_name,
                'last_name': profile.last_name,
                'room': profile.room,
                'degree': profile.degree,
                'department': profile.department,
                'presence': True,
            }
            for profile in profiles
        ]

        formset = AttendanceCheckinFormSet(initial=initial_data, queryset=AttendanceCheckin.objects.none())
        grouped_profiles = profiles.values('room', 'department').distinct()

    return render(request, 'attendance/bulk_checkin.html', {
        'formset': formset,
        'attendance': attendance,
        'grouped_profiles': grouped_profiles,
        'room_filter': room_filter,
        'department_filter': department_filter
    })

class ReportList(ListView):
    model = Attendance
    template_name = 'attendance/report_list.html'
    context_object_name = 'reports'

def attendance_report(request, pk):
    # Fetch attendance record using the pk
    attendance = get_object_or_404(Attendance, pk=pk)

    attendances = Attendance.objects.all()
    progress_reports = {}

    if request.method == 'GET':
        date_checkin = request.GET.get('date_checkin', '').strip()  # Trim whitespace

        # Check date format
        if date_checkin and not parse_date(date_checkin):
            raise ValidationError("วันที่ไม่ถูกต้อง กรุณาใช้รูปแบบ YYYY-MM-DD")

        # Filter attendance data for the selected activity
        attendance_data = AttendanceCheckin.objects.filter(att_name=attendance)

        if date_checkin:
            attendance_data = attendance_data.filter(date_checkin=date_checkin)

        # Update presence status and calculate attendance count and percentage
        attendance_count = {}
        for record in attendance_data:
            presence_status = "Present" if record.presence else "Absent"

            # Count attendance for each student
            student_number = record.student_number

            if student_number not in attendance_count:
                attendance_count[student_number] = {
                    'present': 0,
                    'absent': 0,
                    'name': f"{record.first_name} {record.last_name}",
                    'att_name': attendance.att_name,
                    'room': record.room,
                    'department': record.department,
                }

            # Increment count
            if presence_status == "Present":
                attendance_count[student_number]['present'] += 1
            else:
                attendance_count[student_number]['absent'] += 1

        # Create progress report with percentages
        for student_number, data in attendance_count.items():
            total_attendance = data['present'] + data['absent']
            attendance_percentage = (data['present'] / total_attendance * 100) if total_attendance > 0 else 0
            status = "ผ่าน" if attendance_percentage >= 80 else "ไม่ผ่าน"

            if data['att_name'] not in progress_reports:
                progress_reports[data['att_name']] = []

            progress_reports[data['att_name']].append({
                'student_number': student_number,
                'name': data['name'],
                'room': data['room'],
                'department': data['department'],
                'present': data['present'],
                'absent': data['absent'],
                'percentage': round(attendance_percentage, 2),
                'status': status,
            })

    context = {'attendances': attendances, 'progress_reports': progress_reports}
    return render(request, 'attendance/attendance_report.html', context)

def self_report(request, pk):
    # Fetch attendance record using the pk
    attendance = get_object_or_404(Attendance, pk=pk)

    attendances = Attendance.objects.all()
    progress_reports = {}

    if request.method == 'GET':
        date_checkin = request.GET.get('date_checkin', '').strip()  # Trim whitespace

        # Check date format
        if date_checkin and not parse_date(date_checkin):
            raise ValidationError("วันที่ไม่ถูกต้อง กรุณาใช้รูปแบบ YYYY-MM-DD")

        # Filter attendance data for the selected activity
        attendance_data = AttendanceCheckin.objects.filter(att_name=attendance)

        if date_checkin:
            attendance_data = attendance_data.filter(date_checkin=date_checkin)

        # Update presence status and calculate attendance count and percentage
        attendance_count = {}
        for record in attendance_data:
            presence_status = "Present" if record.presence else "Absent"

            # Count attendance for each student
            student_number = record.student_number

            if student_number not in attendance_count:
                attendance_count[student_number] = {
                    'present': 0,
                    'absent': 0,
                    'name': f"{record.first_name} {record.last_name}",
                    'att_name': attendance.att_name,
                    'room': record.room,
                    'department': record.department,
                }

            # Increment count
            if presence_status == "Present":
                attendance_count[student_number]['present'] += 1
            else:
                attendance_count[student_number]['absent'] += 1

        # Create progress report with percentages
        for student_number, data in attendance_count.items():
            total_attendance = data['present'] + data['absent']
            attendance_percentage = (data['present'] / total_attendance * 100) if total_attendance > 0 else 0
            status = "ผ่าน" if attendance_percentage >= 80 else "ไม่ผ่าน"

            if data['att_name'] not in progress_reports:
                progress_reports[data['att_name']] = []

            progress_reports[data['att_name']].append({
                'student_number': student_number,
                'name': data['name'],
                'room': data['room'],
                'department': data['department'],
                'present': data['present'],
                'absent': data['absent'],
                'percentage': round(attendance_percentage, 2),
                'status': status,
            })

    context = {'attendances': attendances, 'progress_reports': progress_reports}
    return render(request, 'attendance/attendance_report.html', context)

class AttendanceFilter(FilterSet):
    class Meta:
        model = Profile
        fields = ['room', 'degree', 'department']

        labels = {
            'room': '',
            'degree': '',
            'department': '',
        }

def attendancesearch(request):
    filter = AttendanceFilter(request.GET, queryset=AttendanceCheckin.objects.all())
    context = {'filter': filter}
    return render(request, 'attendance/attendance_search.html', context)

def attendance_checkin(request):
    if request.method == 'POST':
        form = CheckinForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('attendance/attendance_report')  # Redirect to a success page or another view
    else:
        form = CheckinForm()

    def get_initial(self):
        initial = super().get_initial()
        profile = self.request.user.profile
        initial['student_number'] = profile.student_number
        initial['first_name'] = profile.first_name
        initial['last_name'] = profile.last_name
        initial['room'] = profile.room
        initial['degree'] = profile.degree
        initial['department'] = profile.department
        return initial
    
    return render(request, 'attendance/attendance.html', {'form': form})









