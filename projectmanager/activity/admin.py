from django.contrib import admin
from base.models import Profile  # Import Profile model
from .models import Organizer, Activity, Ticket, AttendanceCheckin, Attendance

# Organizer Admin
class OrganizerAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner']  # Adjust field names accordingly
    search_fields = ['owner__first_name', 'owner__last_name', 'owner__student_number']  # Search fields must reference Profile fields
    autocomplete_fields = ['owner']  # Use the ForeignKey field name directly

# Register models
admin.site.register(Activity)
admin.site.register(Ticket)
admin.site.register(Attendance)
admin.site.register(AttendanceCheckin)
admin.site.register(Organizer, OrganizerAdmin)