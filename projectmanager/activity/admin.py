from django.contrib import admin
from .models import Organizer, Activity, Ticket,AttendanceCheckin, Attendance
# Register your models here.

admin.site.register(Organizer)
admin.site.register(Activity)
admin.site.register(Ticket)
admin.site.register(Attendance)
admin.site.register(AttendanceCheckin)