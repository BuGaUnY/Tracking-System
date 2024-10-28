from django.contrib import admin
from base.models import Profile  # Import Profile model
from .models import Organizer, Activity, Ticket, AttendanceCheckin, Attendance

# Organizer Admin
class OrganizerAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner'] 
    search_fields = ['owner__first_name', 'owner__last_name', 'owner__student_number'] 
    autocomplete_fields = ['owner']

class AttendanceCheckinAdmin(admin.ModelAdmin):
    list_display = ['att_name' ,'room','department', 'first_name' ,'last_name', 'date_checkin' ] 
    search_fields = ['room', 'department'] 

class TicketAdmin(admin.ModelAdmin):
    list_display = ['room','department', 'activity' ,'profile','date_create'] 
    search_fields = ['room','department', 'activity' ,'profile'] 

# Register models
admin.site.register(Activity)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Attendance)
admin.site.register(AttendanceCheckin, AttendanceCheckinAdmin)
admin.site.register(Organizer, OrganizerAdmin)