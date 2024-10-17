from ckeditor_uploader.fields import RichTextUploadingField
from allauth.socialaccount.models import SocialAccount
from django.urls import reverse
from projectmanager import settings
from linebot.models import *
from linebot.models import FlexSendMessage
from django.core.validators import MinValueValidator, MaxValueValidator
from base.models import Profile
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
from django.db import models
import uuid, os
import qrcode

# Create your models here.
ACTIVITY_CATEGORY = (
    ('1 หน่วยกิจ', '1 หน่วยกิจ'),
    ('2 หน่วยกิจ', '2 หน่วยกิจ'),
)

class Attendance(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    att_name = models.CharField(max_length=50, null=False, default='default_value')

    def get_absolute_url(self):
        return reverse('bulk_checkin', kwargs={'pk': self.pk})

    def get_absolute_report_url(self):
        return reverse('attendance_report', kwargs={'pk': self.pk})
    
    def __str__(self):
        return self.att_name

class AttendanceCheckin(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey('base.Profile' ,on_delete=models.SET_NULL, null=True ,blank=True, related_name='attendance_profile')
    student_number = models.CharField(max_length=20, null=True,blank=True)
    first_name = models.CharField(max_length=100, null=True,blank=True)
    last_name = models.CharField(max_length=100, null=True,blank=True)
    room = models.CharField(max_length=10, null=True,blank=True)
    degree = models.CharField(max_length=10, null=True,blank=True)
    department = models.CharField(max_length=50, null=True,blank=True)
    att_name = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    date_checkin = models.DateField(auto_now=True, blank=False)
    presence = models.BooleanField(default=False)

    class Meta:
        unique_together = (
            'user',
            'att_name',
        )

    def __str__(self):
        return f'{self.att_name} {self.first_name} {self.last_name} {self.department} {self.room} {self.date_checkin} '

    def save(self, *args, **kwargs):
        if self.user:
            # ตรวจสอบว่าโปรไฟล์มีการกำหนดหรือไม่
            if self.user.first_name and self.user.last_name and self.user.student_number:
                self.first_name = self.user.first_name
                self.last_name = self.user.last_name
                self.student_number = self.user.student_number
                self.room = self.user.room
                self.degree = self.user.degree
                self.department = self.user.department
        super().save(*args, **kwargs)

class Organizer(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    owner = models.ForeignKey('base.Profile', on_delete=models.CASCADE, related_name='owner', null=True, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='organizer-image', default='organizer-image/default.png')
    email = models.EmailField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    date_updated = models.DateTimeField(auto_now=True, blank=False)
    date_create = models.DateTimeField(auto_now_add=True, blank=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Check image None
        if not self.image:
            self.image = "organizer-image/default.png"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('organizer-detail', kwargs={'pk': self.pk})
    

    def get_absolute_owner_url(self):
        return reverse('organizer-owner-detail', kwargs={'pk': self.pk})

class Activity(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    image = models.ImageField(upload_to='event-image', default='')
    title = models.CharField(max_length=255)
    description = models.TextField()
    detail = models.TextField()
    activity_category = models.CharField(max_length=20, choices=ACTIVITY_CATEGORY)
    organizer = models.ForeignKey(Organizer, null=True, on_delete=models.SET_NULL)
    organizer1 = models.ForeignKey(Organizer, null=True, blank=True, on_delete=models.SET_NULL, related_name='activities_as_organizer1')
    organizer2 = models.ForeignKey(Organizer, null=True, blank=True, on_delete=models.SET_NULL, related_name='activities_as_organizer2')
    organizer3 = models.ForeignKey(Organizer, null=True, blank=True, on_delete=models.SET_NULL, related_name='activities_as_organizer3')
    organizer4 = models.ForeignKey(Organizer, null=True, blank=True, on_delete=models.SET_NULL, related_name='activities_as_organizer4')
    organizer5 = models.ForeignKey(Organizer, null=True, blank=True, on_delete=models.SET_NULL, related_name='activities_as_organizer5')
    organizer6 = models.ForeignKey(Organizer, null=True, blank=True, on_delete=models.SET_NULL, related_name='activities_as_organizer6')
    organizer7 = models.ForeignKey(Organizer, null=True, blank=True, on_delete=models.SET_NULL, related_name='activities_as_organizer7')
    organizer8 = models.ForeignKey(Organizer, null=True, blank=True, on_delete=models.SET_NULL, related_name='activities_as_organizer8')
    organizer9 = models.ForeignKey(Organizer, null=True, blank=True, on_delete=models.SET_NULL, related_name='activities_as_organizer9')
    date_start = models.DateTimeField(null=True, blank=True)
    status = models.BooleanField(default=True)
    date_updated = models.DateTimeField(auto_now=True, blank=False)
    date_create = models.DateTimeField(auto_now_add=True, blank=False)

    def __str__(self):
        return f'{self.title} - {self.activity_category}'

    def get_absolute_url(self):
        return reverse('activity-detail', kwargs={'pk': self.pk})

    def get_absolute_owner_activity_checkin_url(self):
        return reverse('organizer-owner-activity-checkin', kwargs={'organizer_pk': self.organizer.pk, 'activity_pk': self.pk})

    def get_absolute_organizer_owner_activity_ticket_list_url(self):
        return reverse('organizer-owner-activity-ticket-list', kwargs={'pk': self.pk})
    
class Ticket(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    activity = models.ForeignKey(Activity, on_delete=models.SET_NULL, null=True)
    profile = models.ForeignKey('base.Profile', on_delete=models.SET_NULL, null=True, blank=True, related_name='ticket_profile')
    student_number = models.CharField(max_length=20, null=True) 
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    room = models.CharField(max_length=5, null=True)
    degree = models.CharField(max_length=20, null=True)
    department = models.CharField(max_length=100, null=True)
    qrcode = models.ImageField(upload_to='ticket-qrcode', default='', null=True, blank=True)
    checkin = models.BooleanField(default=False)
    date_updated = models.DateTimeField(auto_now=True, blank=False)
    date_create = models.DateTimeField(auto_now_add=True, blank=False)

    @property
    def activity_category(self):
        return self.activity.activity_category if self.activity else None
    
    class Meta:
        unique_together = ('activity', 'profile')

    def __str__(self):
        return f'{self.profile} - {self.activity}'

    def save(self, *args, **kwargs):
        # Generate a QR code for the ticket
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.uid)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save the QR code image
        with open(f'media/ticket-qrcode/{self.uid}.png', 'wb') as f:
            img.save(f)
        
        self.qrcode = f'ticket-qrcode/{self.uid}.png'  
        super().save(*args, **kwargs)  # Ensure the base save method is called

    def get_absolute_url(self):
        return reverse('ticket-detail', kwargs={'pk': self.pk})
    
    def get_absolute_update_url(self):
        return reverse('ticket-update', kwargs={'pk': self.pk})
    