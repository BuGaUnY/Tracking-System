from django.contrib import admin
from .models import Profile
# Register your models here.
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['room','department','first_name', 'last_name', 'student_number']
    search_fields = ['room','department','first_name', 'last_name', 'student_number']

admin.site.register(Profile, ProfileAdmin)
