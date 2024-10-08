from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
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
from django.http import HttpResponse, HttpResponseBadRequest, Http404 ,HttpResponseNotAllowed, JsonResponse
from django.utils import timezone
from django.forms.models import modelformset_factory
from django.core.exceptions import ValidationError, ObjectDoesNotExist
import logging , uuid , re
from openpyxl import Workbook
from django.views import View

logger = logging.getLogger(__name__)

# Create your views here.

def is_valid_uuid(value):
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False
    
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

        # Debug logging to check the received values
        logger.debug(f"Received org_pk: {org_pk}, act_pk: {act_pk}")

        # Validate if both primary keys are valid
        try:
            Organizer.objects.get(pk=org_pk)
            Activity.objects.get(pk=act_pk)
        except (Organizer.DoesNotExist, Activity.DoesNotExist) as e:
            logger.error(f"Invalid primary key: {str(e)}")
            return JsonResponse({'success': False, 'error': 'Invalid organizer or activity ID'}, status=400)

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

class TicketCheckin(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        logger.info("POST request received for ticket check-in")
        
        activity_uid = request.POST.get('activity_uid')
        ticket_uid = request.POST.get('ticket_uid')

        logger.debug(f"Received activity_uid: {activity_uid}, ticket_uid: {ticket_uid}")

        # Regular expression to validate UUID format
        uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')

        if not activity_uid or not ticket_uid:
            logger.error("Missing activity_uid or ticket_uid")
            return JsonResponse({'success': False, 'error': 'Missing activity_uid or ticket_uid'}, status=400)

        if not uuid_pattern.match(activity_uid) or not uuid_pattern.match(ticket_uid):
            logger.error(f"Invalid UUID format for activity_uid: {activity_uid} or ticket_uid: {ticket_uid}")
            return JsonResponse({'success': False, 'error': 'Invalid UUID format'}, status=400)

        try:
            activity = Activity.objects.get(uid=activity_uid)
            logger.info(f"Activity found: {activity.uid}")
        except Activity.DoesNotExist:
            logger.error(f"Activity not found with uid: {activity_uid}")
            return JsonResponse({'success': False, 'error': 'Activity not found'}, status=404)

        try:
            ticket = Ticket.objects.get(uid=ticket_uid, activity=activity)
            logger.info(f"Ticket found: {ticket.uid}")
            return JsonResponse({'success': True, 'ticket_uid': ticket.uid})
        except Ticket.DoesNotExist:
            logger.error(f"Ticket not found with uid: {ticket_uid} for activity: {activity_uid}")
            return JsonResponse({'success': False, 'error': 'Ticket not found'}, status=404)

# View ที่ใช้ดึงข้อมูลมาแสดงใน partial
def post(self, request, *args, **kwargs):
    if request.htmx:
        # ค้นหา Activity จาก activity_uid
        try:
            activity = Activity.objects.get(uid=request.POST['activity_uid'])
        except Activity.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Activity not found'})

        # ค้นหา Ticket จาก ticket_uid และ activity
        try:
            ticket = Ticket.objects.get(uid=request.POST['ticket_uid'], activity=activity)
        except Ticket.DoesNotExist:
            ticket = None

        # Render partial view พร้อมกับข้อมูลของ ticket
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
    rooms = set()
    departments = set()

    # Get filters from the request
    room_filter = request.GET.get('room', '').strip()
    department_filter = request.GET.get('department', '').strip()
    date_checkin = request.GET.get('date_checkin', '').strip()

    if request.method == 'GET':
        if date_checkin and not parse_date(date_checkin):
            raise ValidationError("วันที่ไม่ถูกต้อง กรุณาใช้รูปแบบ YYYY-MM-DD")

        # Fetch attendance data and apply date filter
        attendance_data = AttendanceCheckin.objects.filter(att_name=attendance)
        if date_checkin:
            attendance_data = attendance_data.filter(date_checkin=date_checkin)

        # Apply room and department filters if selected
        if room_filter:
            attendance_data = attendance_data.filter(room=room_filter)
        if department_filter:
            attendance_data = attendance_data.filter(department=department_filter)

        attendance_count = {}
        for record in attendance_data:
            student_number = record.student_number
            presence_status = "Present" if record.presence else "Absent"

            if student_number not in attendance_count:
                attendance_count[student_number] = {
                    'present': 0,
                    'absent': 0,
                    'name': f"{record.first_name} {record.last_name}",
                    'att_name': attendance.att_name,
                    'room': record.room,
                    'department': record.department,
                }

            if presence_status == "Present":
                attendance_count[student_number]['present'] += 1
            else:
                attendance_count[student_number]['absent'] += 1

            # Collect rooms and departments for filtering
            rooms.add(record.room)
            departments.add(record.department)

        # Prepare progress report with attendance percentage
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

    context = {
        'attendances': attendances,
        'progress_reports': progress_reports,
        'rooms': sorted(rooms),  # sorted to display rooms in order
        'departments': sorted(departments),  # sorted to display departments in order
        'room_filter': room_filter,
        'department_filter': department_filter,
        'date_checkin': date_checkin,
    }
    return render(request, 'attendance/attendance_report.html', context)

ACTIVITY_MAP = {
    'กิจกรรมเข้าแถว': 'line_up',
    'กิจกรรมชมรม': 'club',
    'กิจกรรมโฮมรูม': 'homeroom',
    'กิจกรรมลูกเสือ': 'scout'
}

def sum_report(request):
    # ดึงข้อมูลการเข้าร่วมทั้งหมด
    attendances = Attendance.objects.all()
    progress_reports = {}
    rooms = set()
    departments = set()

    # รับค่ากรองจาก request
    room_filter = request.GET.get('room', '').strip()
    department_filter = request.GET.get('department', '').strip()
    date_checkin = request.GET.get('date_checkin', '').strip()

    if request.method == 'GET':
        if date_checkin and not parse_date(date_checkin):
            raise ValidationError("วันที่ไม่ถูกต้อง กรุณาใช้รูปแบบ YYYY-MM-DD")

        # วนลูปเพื่อดึงข้อมูลการเข้าร่วมแต่ละกิจกรรม
        for attendance in attendances:
            attendance_data = AttendanceCheckin.objects.filter(att_name=attendance)

            # กรองวันที่ถ้ามี
            if date_checkin:
                attendance_data = attendance_data.filter(date_checkin=date_checkin)

            # กรองห้องและแผนกถ้ามี
            if room_filter:
                attendance_data = attendance_data.filter(room=room_filter)
            if department_filter:
                attendance_data = attendance_data.filter(department=department_filter)

            # เก็บข้อมูลนักเรียนแต่ละคนและสถานะกิจกรรม
            for record in attendance_data:
                student_number = record.student_number

                # ถ้ายังไม่มีข้อมูลนักเรียนใน progress_reports ให้เพิ่ม
                if student_number not in progress_reports:
                    progress_reports[student_number] = {
                        'name': f"{record.first_name} {record.last_name}",
                        'room': record.room,
                        'department': record.department,
                        'activities': {
                            'line_up': '-',
                            'club': '-',
                            'homeroom': '-',
                            'scout': '-',
                        }
                    }

                # อัปเดตสถานะกิจกรรมใน activities ของนักเรียน
                presence_status = "ผ่าน" if record.presence else "ไม่ผ่าน"
                progress_reports[student_number]['activities'][ACTIVITY_MAP[attendance.att_name]] = presence_status

                # รวบรวมห้องและแผนกสำหรับการกรอง
                rooms.add(record.room)
                departments.add(record.department)

    context = {
        'progress_reports': progress_reports,
        'rooms': sorted(rooms),
        'departments': sorted(departments),
        'room_filter': room_filter,
        'department_filter': department_filter,
        'date_checkin': date_checkin,
    }
    return render(request, 'attendance/sum_report.html', context)

def export_to_excel(request):
    # ดึงข้อมูลการเข้าร่วมทั้งหมด
    attendances = Attendance.objects.all()
    progress_reports = {}
    
    # รับค่ากรองจาก request
    room_filter = request.GET.get('room', '').strip()
    department_filter = request.GET.get('department', '').strip()
    date_checkin = request.GET.get('date_checkin', '').strip()

    # วนลูปเพื่อดึงข้อมูลการเข้าร่วมแต่ละกิจกรรม
    for attendance in attendances:
        attendance_data = AttendanceCheckin.objects.filter(att_name=attendance)

        # กรองวันที่ถ้ามี
        if date_checkin:
            attendance_data = attendance_data.filter(date_checkin=date_checkin)

        # กรองห้องและแผนกถ้ามี
        if room_filter:
            attendance_data = attendance_data.filter(room=room_filter)
        if department_filter:
            attendance_data = attendance_data.filter(department=department_filter)

        # เก็บข้อมูลนักเรียนแต่ละคนและสถานะกิจกรรม
        for record in attendance_data:
            student_number = record.student_number

            # ถ้ายังไม่มีข้อมูลนักเรียนใน progress_reports ให้เพิ่ม
            if student_number not in progress_reports:
                progress_reports[student_number] = {
                    'name': f"{record.first_name} {record.last_name}",
                    'room': record.room,
                    'department': record.department,
                    'activities': {
                        'line_up': '-',
                        'club': '-',
                        'homeroom': '-',
                        'scout': '-',
                    }
                }

            # อัปเดตสถานะกิจกรรมใน activities ของนักเรียน
            presence_status = "ผ่าน" if record.presence else "ไม่ผ่าน"
            progress_reports[student_number]['activities'][ACTIVITY_MAP[attendance.att_name]] = presence_status

    # สร้าง workbook ใหม่
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'รายงานความก้าวหน้า'

    # เขียนหัวตาราง
    worksheet.append(['รหัสประจำตัว', 'ชื่อ-สกุล', 'แผนก/ชั้น/กลุ่ม', 'กิจกรรมเข้าแถว', 'กิจกรรมชมรม', 'กิจกรรมโฮมรูม', 'กิจกรรมลูกเสือ'])

    # เขียนข้อมูลลงใน worksheet
    for student_number, details in progress_reports.items():
        worksheet.append([
            student_number,
            details['name'],
            f"{details['room']} {details['department']}",
            details['activities']['line_up'],
            details['activities']['club'],
            details['activities']['homeroom'],
            details['activities']['scout'],
        ])

    # สร้าง HttpResponse สำหรับส่งออกไฟล์ Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="progress_report.xlsx"'
    workbook.save(response)

    return response


@login_required
def self_report(request):
    # Get the currently logged-in user's profile
    user_profile = get_object_or_404(Profile, user=request.user)
    
    # Fetch attendance records for the user's profile
    attendance_records = AttendanceCheckin.objects.filter(student_number=user_profile.student_number)

    # Dictionary to hold attendance summary per activity
    attendance_summary = {}

    # Aggregate attendance data for each activity
    for record in attendance_records:
        if record.att_name not in attendance_summary:
            attendance_summary[record.att_name] = {
                'present': 0,
                'absent': 0,
            }

        if record.presence:  # Assuming presence is a boolean field
            attendance_summary[record.att_name]['present'] += 1
        else:
            attendance_summary[record.att_name]['absent'] += 1

    # Calculate percentage and status for each activity
    for activity, data in attendance_summary.items():
        total = data['present'] + data['absent']
        attendance_percentage = (data['present'] / total * 100) if total > 0 else 0
        status = "ผ่าน" if attendance_percentage >= 80 else "ไม่ผ่าน"
        data.update({
            'attendance_percentage': attendance_percentage,
            'status': status,
            'activity': activity,
        })

    return render(request, 'attendance/self_report.html', {
        'attendance_summary': attendance_summary.values(),  # Pass the summary as a list
        'user_profile': user_profile,
    })
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










