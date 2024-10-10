from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils.dateparse import parse_date
from django.db.models import Count, Q , Case, When, IntegerField
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView
from .models import Activity, Organizer , Attendance, AttendanceCheckin, Ticket
from base.models import Profile
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from .forms import TicketForm, AttendanceCheckinForm
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
from django.db import transaction

logger = logging.getLogger(__name__)


def is_valid_uuid(value):
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False

class Teacher(LoginRequiredMixin,ListView):
    model = Organizer
    template_name = 'activity/teacher.html'
    context_object_name = 'teachers'
    ordering = ['-date_create']
    
    def get_queryset(self):
        return Organizer.objects.filter(owner=self.request.user.profile)

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

class ActivityFilter(django_filters.FilterSet):
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
        initial['student_number'] = profile.student_number
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
    def get(self, request, *args, **kwargs):
        # ดึงค่าพารามิเตอร์จาก GET request
        activity_uid = request.GET.get('activity_uid')
        ticket_uid = request.GET.get('ticket_uid')

        # ตรวจสอบว่ามีการส่งค่าทั้งสองตัวเข้ามาหรือไม่
        if not activity_uid or not ticket_uid:
            return JsonResponse({'success': False, 'error': 'Missing activity_uid or ticket_uid'}, status=400)

        # พยายามค้นหา Activity และ Ticket
        try:
            activity = Activity.objects.get(uid=activity_uid)
            ticket = Ticket.objects.get(uid=ticket_uid, activity=activity)
        except Activity.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Activity not found'}, status=404)
        except Ticket.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Ticket not found'}, status=404)

        # ถ้าพบทั้ง Activity และ Ticket ให้ส่งข้อมูลไปยัง template
        return render(request, 'activity/partials/ticket-checkin.html', {'ticket': ticket})

class TicketCheckinSuccessView(View):
    def post(self, request, *args, **kwargs):
        ticket_uid = request.POST.get('ticket_uid')

        # Get the ticket or return a 404 error if it doesn't exist
        ticket = get_object_or_404(Ticket.objects.select_for_update(), uid=ticket_uid)

        with transaction.atomic():
            print(f"Before checkin: {ticket.checkin}")

            if not ticket.checkin:
                ticket.checkin = True  # Update check-in status
                ticket.save()
                print(f"After save: {ticket.checkin}")

                # Refresh the ticket from the database to ensure the value is updated
                ticket.refresh_from_db()
                print(f"Refreshed checkin status after refresh: {ticket.checkin}")  # Check if it's updated correctly

                return render(request, 'activity/partials/ticket-checkin.html', {'ticket': ticket})
            else:
                return JsonResponse({'success': False, 'message': 'Ticket already checked in.'}, status=400)

class AttendanceList(ListView):
    model = Attendance
    template_name = 'attendance/attendance_list.html'
    context_object_name = 'attendances'


def bulk_checkin(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)  # ค้นหาบันทึกการเข้าร่วม
    room_filter = request.GET.get('room')
    department_filter = request.GET.get('department')

    # เริ่มต้นด้วยการดึงโปรไฟล์ทั้งหมด
    profiles = Profile.objects.all()

    # กรองโปรไฟล์ตามห้องและแผนก
    if room_filter:
        profiles = profiles.filter(room=room_filter)

    if department_filter:
        profiles = profiles.filter(department=department_filter)

    # สร้าง FormSet สำหรับการบันทึก AttendanceCheckin
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

            return redirect('report_list')  # เปลี่ยนเส้นทางไปยังหน้ารายงานหลังจากบันทึกข้อมูล

    else:
        # สร้างข้อมูลเริ่มต้นสำหรับฟอร์ม
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

        # สร้างฟอร์มเซ็ตด้วยข้อมูลเริ่มต้นและไม่ใช้ queryset
        formset = AttendanceCheckinFormSet(initial=initial_data, queryset=AttendanceCheckin.objects.none())

        # จัดกลุ่มโปรไฟล์ตามห้องและแผนกเพื่อแสดงใน template
        # ทำให้ห้องไม่ซ้ำกันและเรียงตามลำดับที่ต้องการ (1-9, A-Z)
        grouped_profiles = profiles.values('room', 'department').distinct().order_by(
            Case(
                When(room__regex=r'^[0-9]+$', then=1),  # ห้องที่เป็นตัวเลข
                When(room__regex=r'^[A-Za-z]+$', then=2),  # ห้องที่เป็นตัวอักษร
                output_field=IntegerField(),
            )
        ).order_by('room')  # เรียงตามชื่อห้อง

        # เช็คว่ามีโปรไฟล์อยู่ใน department filter หรือไม่
        if department_filter:
            print(f"Filtering by department: {department_filter}. Remaining profiles: {profiles.count()}")

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
    rooms = set()  # Use a set to collect unique rooms
    departments = set()

    # Get filters from the request
    room_filter = request.GET.get('room', '').strip()
    department_filter = request.GET.get('department', '').strip()
    date_checkin = request.GET.get('date_checkin', '').strip()

    if request.method == 'GET':
        # Validate the date format
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

            # Increment present or absent count
            if presence_status == "Present":
                attendance_count[student_number]['present'] += 1
            else:
                attendance_count[student_number]['absent'] += 1

            # Collect unique rooms and departments for filtering
            rooms.add(record.room)
            departments.add(record.department)

        # Prepare progress report with attendance percentage
        for student_number, data in attendance_count.items():
            total_attendance = data['present'] + data['absent']
            attendance_percentage = (data['present'] / total_attendance * 100) if total_attendance > 0 else 0
            status = "ผ่าน" if attendance_percentage >= 60 else "ไม่ผ่าน"

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

    # Remove duplicates and sort rooms and departments
    sorted_rooms = sorted(rooms, key=lambda x: (x.isdigit(), x))  # Unique rooms sorted
    sorted_departments = sorted(set(departments))  # Unique departments sorted

    context = {
        'attendances': attendances,
        'progress_reports': progress_reports,
        'rooms': sorted(set(sorted_rooms)),  # Ensure uniqueness before sorting
        'departments': sorted_departments,
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


@login_required
def sum_report(request):
    # Get the user's profile to access the student_number
    user_profile = get_object_or_404(Profile, user=request.user)
    student_number = user_profile.student_number  # Get the student number from the user's profile
    ticket_records = Ticket.objects.filter(student_number=student_number)  # Fetch tickets for the user

    # ดึงบันทึกการเข้าร่วมทั้งหมด
    attendances = Attendance.objects.all()
    progress_reports = {}
    rooms = set()  # เซ็ตสำหรับเก็บห้อง
    departments = set()  # เซ็ตสำหรับเก็บแผนก

    # รับค่าตัวกรองจากคำขอ
    room_filter = request.GET.get('room', '').strip()
    department_filter = request.GET.get('department', '').strip()
    date_checkin = request.GET.get('date_checkin', '').strip()

    if request.method == 'GET':
        # ตรวจสอบความถูกต้องของรูปแบบวันที่
        if date_checkin and not parse_date(date_checkin):
            raise ValidationError("วันที่ไม่ถูกต้อง กรุณาใช้รูปแบบ YYYY-MM-DD")

        # วนลูปผ่านบันทึกการเข้าร่วม
        for attendance in attendances:
            attendance_data = AttendanceCheckin.objects.filter(att_name=attendance)

            # ใช้ตัวกรองถ้ามี
            if date_checkin:
                attendance_data = attendance_data.filter(date_checkin=date_checkin)
            if room_filter:
                attendance_data = attendance_data.filter(room=room_filter)
            if department_filter:
                attendance_data = attendance_data.filter(department=department_filter)

            # ประมวลผลบันทึกการเข้าร่วม
            for record in attendance_data:
                student_number = record.student_number

                # เพิ่มนักเรียนไปยัง progress_reports หากยังไม่เคยมีมาก่อน
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
                        },
                        'unit_count': 0,  # เริ่มต้นนับหน่วยกิจกรรมสำหรับนักเรียน
                        'status': '-'  # สถานะเริ่มต้นเป็น 'ไม่ผ่าน'
                    }

                # อัปเดตสถานะการเข้าร่วมสำหรับกิจกรรม
                presence_status = "ผ่าน" if record.presence else "ไม่ผ่าน"
                progress_reports[student_number]['activities'][ACTIVITY_MAP[attendance.att_name]] = presence_status

                # เก็บห้องและแผนกสำหรับการกรอง
                rooms.add(record.room)
                departments.add(record.department)

    # สรุปข้อมูลตั๋ว
    ticket_summary = {}
    total_units = 0  # หน่วยรวมที่นับได้จากการเข้าร่วมกิจกรรมตั๋ว

    # รวมข้อมูลการเช็คอินตั๋ว
    for ticket in ticket_records:
        activity = ticket.activity
        if activity not in ticket_summary:
            ticket_summary[activity] = {
                'total_tickets': 0,
                'checked_in': 0,
            }

        ticket_summary[activity]['total_tickets'] += 1
        if ticket.checkin:
            ticket_summary[activity]['checked_in'] += 1
            
            # เพิ่มหน่วยรวมตามหมวดหมู่กิจกรรม
            if ticket.activity.activity_category == '2 หน่วยกิจ':
                total_units += 2  # 2 หน่วยสำหรับกิจกรรมใหญ่
            elif ticket.activity.activity_category == '1 หน่วยกิจ':
                total_units += 1  # 1 หน่วยสำหรับกิจกรรมเล็ก

    # คำนวณสถานะการเช็คอินตั๋ว
    for activity, data in ticket_summary.items():
        total_tickets = data['total_tickets']
        checked_in_count = data['checked_in']
        
        # ตรวจสอบว่าผู้ใช้ได้เช็คอินตั๋วทั้งหมดหรือไม่
        if total_tickets > 0 and checked_in_count == total_tickets:
            status = "✅ยืนยันแล้ว"  # เช็คอินตั๋วทั้งหมดแล้ว
        else:
            status = "❌ยังไม่ยืนยัน"  # ยังไม่เช็คอินตั๋วทั้งหมด
            
        data.update({
            'checked_in_percentage': (checked_in_count / total_tickets * 100) if total_tickets > 0 else 0,
            'status': status,
            'activity': activity,
        })

    # กำหนดสถานะโดยรวมตามหน่วยกิจกรรมรวม
    overall_status = "-"  # สถานะเริ่มต้น
    if total_units >= 6:
        overall_status = "ผ่าน"
    else:  # ผู้ใช้เข้าร่วมกิจกรรมเพียงพอ
        overall_status = "ไม่ผ่าน"
    ticket_summary[student_number] = overall_status

    # เพิ่มข้อมูลรวมลงใน context
    valid_progress_reports = {
        student_number: report
        for student_number, report in progress_reports.items()
        if student_number is not None  # ตรวจสอบว่า key ไม่เป็น None
    }
    
    context = {
        'progress_reports': dict(sorted(valid_progress_reports.items(), key=lambda item: (int(item[0]) if item[0].isdigit() else float('inf'), item[0]))),  # จัดเรียง student_number
        'rooms': sorted(rooms),
        'departments': sorted(departments),
        'room_filter': room_filter,
        'department_filter': department_filter,
        'date_checkin': date_checkin,
        'ticket_summary': ticket_summary,
        'total_units': total_units,  # ส่งหน่วยรวมสำหรับการแสดงผล
        'overall_status': overall_status,  # ส่งสถานะโดยรวม
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
    # ดึงข้อมูลผู้ใช้
    user_profile = get_object_or_404(Profile, user=request.user)
    
    # ดึงบันทึกการเข้าร่วมสำหรับโปรไฟล์ของผู้ใช้
    attendance_records = AttendanceCheckin.objects.filter(student_number=user_profile.student_number)

    # ดึงบันทึกตั๋วสำหรับโปรไฟล์ของผู้ใช้
    ticket_records = Ticket.objects.filter(profile=user_profile)

    # พจนานุกรมสำหรับสรุปการเข้าร่วมตามกิจกรรม
    attendance_summary = {}
    
    # รวมข้อมูลการเข้าร่วมสำหรับแต่ละกิจกรรม
    for record in attendance_records:
        if record.att_name not in attendance_summary:
            attendance_summary[record.att_name] = {
                'present': 0,
                'absent': 0,
            }

        if record.presence:  # สมมติว่า presence เป็นฟิลด์บูลีน
            attendance_summary[record.att_name]['present'] += 1
        else:
            attendance_summary[record.att_name]['absent'] += 1

    # คำนวณเปอร์เซ็นต์และสถานะสำหรับแต่ละกิจกรรม
    for activity, data in attendance_summary.items():
        total = data['present'] + data['absent']
        attendance_percentage = (data['present'] / total * 100) if total > 0 else 0
        status = "ผ่าน" if attendance_percentage >= 60 else "ไม่ผ่าน"
        data.update({
            'attendance_percentage': attendance_percentage,
            'status': status,
            'activity': activity,
        })

    # สรุปข้อมูลตั๋ว
    ticket_summary = {}
    total_units = 0  # หน่วยรวมที่นับได้จากการเข้าร่วมกิจกรรมตั๋ว

    # รวมข้อมูลการเช็คอินตั๋ว
    for ticket in ticket_records:
        if ticket.activity not in ticket_summary:
            ticket_summary[ticket.activity] = {
                'total_tickets': 0,
                'checked_in': 0,
            }

        ticket_summary[ticket.activity]['total_tickets'] += 1
        if ticket.checkin:
            ticket_summary[ticket.activity]['checked_in'] += 1
            # เพิ่มหน่วยรวมตามหมวดหมู่กิจกรรม
            if ticket.activity.activity_category == '2 หน่วยกิจ':
                total_units += 2  # 2 หน่วยสำหรับกิจกรรมใหญ่
            elif ticket.activity.activity_category == '1 หน่วยกิจ':
                total_units += 1  # 1 หน่วยสำหรับกิจกรรมเล็ก

    # คำนวณสถานะการเช็คอินตั๋ว
    for activity, data in ticket_summary.items():
        total_tickets = data['total_tickets']
        checked_in_count = data['checked_in']
        
        # ตรวจสอบว่าผู้ใช้ได้เช็คอินตั๋วทั้งหมดหรือไม่
        if total_tickets > 0 and checked_in_count == total_tickets:
            status = "✅ยืนยันแล้ว"  # เช็คอินตั๋วทั้งหมดแล้ว
        else:
            status = "❌ยังไม่ยืนยัน"  # ยังไม่เช็คอินตั๋วทั้งหมด
            
        data.update({
            'checked_in_percentage': (checked_in_count / total_tickets * 100) if total_tickets > 0 else 0,
            'status': status,
            'activity': activity,
        })

    # กำหนดสถานะโดยรวมตามหน่วยกิจกรรมรวม
    overall_status = "ไม่ผ่าน"  # สถานะเริ่มต้น
    if total_units >= 6:
        overall_status = "ผ่าน"  # ผู้ใช้เข้าร่วมกิจกรรมเพียงพอ

    return render(request, 'attendance/self_report.html', {
        'attendance_summary': attendance_summary.values(),  # ส่งสรุปเป็นรายการ
        'ticket_summary': ticket_summary.values(),  # ส่งสรุปตั๋วเป็นรายการ
        'user_profile': user_profile,
        'total_units': total_units,  # ส่งหน่วยรวมสำหรับการแสดงผล
        'overall_status': overall_status,  # ส่งสถานะโดยรวม
    })














