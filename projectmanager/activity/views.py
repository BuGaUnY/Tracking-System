from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView
from .models import Activity, Organizer, Ticket , Attendance, AttendanceCheckin
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
from django.http import HttpResponse
from django.utils import timezone
import csv

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

class TicketCheckin(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if request.htmx:
            activity = Activity.objects.get(uid=request.POST['activity_uid'])
            try:
                ticket = Ticket.objects.get(uid=request.POST['ticket_uid'] , activity = activity)
            except Ticket.DoesNotExist:
                ticket = None
            return render(request, 'activity/partials/ticket-detail-partials.html', {'ticket': ticket})

class TicketCheckinSuccess(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if request.htmx:
            ticket = get_object_or_404(Ticket, uid=request.POST['ticket_uid'])
            print(ticket)
            ticket.checkin = True
            ticket.save()
            return render(request, 'activity/partials/ticket-detail-partials.html', {'ticket': ticket})

def attendance_checkin(request):
    rooms = Profile.objects.values_list('room', flat=True).distinct()
    departments = Profile.objects.values_list('department', flat=True).distinct()
    att_names = Attendance.objects.values_list('att_name', flat=True).distinct()

    room = request.GET.get('room')
    department = request.GET.get('department')
    att_name = request.GET.get('att_name')
    date_checkin = request.GET.get('date_checkin') 

    checkins = AttendanceCheckin.objects.all()

    if room:
        checkins = checkins.filter(room=room)
    if department:
        checkins = checkins.filter(department=department)
    if att_name:
        checkins = checkins.filter(att_name=att_name)
    if date_checkin:
        checkins = checkins.filter(date_checkin=date_checkin)

    context = {
        'checkins': checkins,
        'rooms': rooms,
        'departments': departments,
        'att_names': att_names,
        'selected_room': room,
        'selected_department': department,
        'selected_att_name': att_name,
        'selected_date_checkin': date_checkin, 
    }
    return render(request, 'attendance/attendance_checkin.html', context)


def attendance_checkin_success(request):
    return render(request, 'attendance/attendance_checkin_success.html')

def attendance_report(request):
    attendances = Attendance.objects.all()  # Fetch all attendances for reference (optional)
    attendance_data = None  # Initialize as None

    if request.method == 'GET':
        att_name = request.GET.get('att_name', '')  # Get selected course
        date_checkin = request.GET.get('date_checkin', '')  # Get selected date

        if att_name:
            attendance_data = AttendanceCheckin.objects.filter(
                att_name__pk=att_name,
                date_checkin=date_checkin
            ).select_related('att_name')
        else:
            attendance_data = AttendanceCheckin.objects.filter(date_checkin=date_checkin).select_related('att_name') if date_checkin else AttendanceCheckin.objects.all().select_related('att_name')

        # Update presence status based on the condition
        for attendance in attendance_data:
            attendance.presence = "Present" if attendance.presence == 1 else "Absent"

    context = {'attendances': attendances, 'attendance_data': attendance_data}
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










