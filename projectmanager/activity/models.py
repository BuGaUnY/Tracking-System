from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from allauth.socialaccount.models import SocialAccount
from django.urls import reverse
from projectmanager import settings
from linebot import LineBotApi
from linebot.models import *
import uuid
import qrcode
from linebot.models import FlexSendMessage
from django.core.validators import MinValueValidator, MaxValueValidator
from base.models import Profile

line_bot_api = LineBotApi(settings.channel_access_token)
# Create your models here.
ACTIVITY_CATEGORY = (
    ('กิจกรรมพิเศษ', 'กิจกรรมพิเศษ'),
    ('กิจกรรมเข้าแถว', 'กิจกรรมเข้าแถว'),
    ('กิจกรรมชมรม', 'กิจกรรมชมรม'),
    ('กิจกรรมโฮมรูม', 'กิจกรรมโฮมรูม'),
    ('กิจกรรมลูกเสือ', 'กิจกรรมลูกเสือ'),
    ('กิจกรรม ร.ด.', 'กิจกรรม ร.ด.'),
)


class Attendance(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    att_name = models.CharField(max_length=50)
    credits = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    def __str__(self):
        return self.att_name

profiles = Profile.objects.all()
for profile in profiles:
    first_name = profile.first_name
    last_name = profile.last_name
    student_number = profile.student_number
    room = profile.room
    degree = profile.degree
    department = profile.department
class AttendanceCheckin(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey('base.Profile' ,on_delete=models.SET_NULL, null=True ,blank=True, related_name='attendance_profile')
    student_number = models.CharField(max_length=20,)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    room = models.CharField(max_length=10)
    degree = models.CharField(max_length=10)
    department = models.CharField(max_length=50)
    att_name = models.ForeignKey(Attendance, related_name='checkins', null=True, on_delete=models.SET_NULL)
    date_checkin = models.DateTimeField(null=True, blank=True)
    presence = models.IntegerField(choices=[(0, 'Absent'), (1, 'Present')], default=1)

    class Meta:
        unique_together = ('user','att_name',
        )

    def __str__(self):
        return f'{self.att_name} {self.first_name} {self.last_name} {self.date_checkin}'

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
    website = models.URLField(max_length=255, null=True, blank=True)
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
    activity_category = models.CharField(max_length=20, null=True, choices=ACTIVITY_CATEGORY, blank=True)
    organizer = models.ForeignKey(Organizer, null=True, on_delete=models.SET_NULL)
    date_start = models.DateTimeField(null=True, blank=True)
    status = models.BooleanField(default=True)
    date_updated = models.DateTimeField(auto_now=True, blank=False)
    date_create = models.DateTimeField(auto_now_add=True, blank=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('activity-detail', kwargs={'pk': self.pk})

    def get_absolute_owner_activity_checkin_url(self):
        return reverse('organizer-owner-activity-checkin', kwargs={'organizer_pk': self.organizer.pk, 'activity_pk': self.pk})

    def get_absolute_organizer_owner_activity_ticket_list_url(self):
        return reverse('organizer-owner-activity-ticket-list', kwargs={'pk': self.pk})
    
class Ticket(models.Model):
    uid = models.UUIDField(default = uuid.uuid4, editable=False, unique=True)
    activity = models.ForeignKey(Activity ,on_delete=models.SET_NULL, null=True)
    profile = models.ForeignKey('base.Profile' ,on_delete=models.SET_NULL, null=True ,blank=True, related_name='ticket_profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    room = models.CharField(max_length=10)
    degree = models.CharField(max_length=20)
    department = models.CharField(max_length=100)
    checkin = models.BooleanField(default=False)
    qrcode = models.ImageField(upload_to='ticket-qrcode', default='', null=True, blank=True)
    date_updated = models.DateTimeField(auto_now=True, blank=False)
    date_create = models.DateTimeField(auto_now_add=True, blank=False)

    class Meta:
        unique_together = (
            'activity',
            'profile',
        )

    def __str__(self):
        return f'{self.profile} - {self.activity}'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_checkin = self.checkin
    
    def save(self, *args, **kwargs):
        qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
        qr.add_data(self.uid)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        with open(f'media/ticket-qrcode/{self.uid}.png', 'wb') as f:
            img.save(f)
        self.qrcode = f'ticket-qrcode/{self.uid}.png'
        if self.checkin == True and self.__original_checkin == False:
            social_user = SocialAccount.objects.get(user=self.profile.user)
            flex_message = FlexSendMessage(
                alt_text='Checkin',
                contents={
                        "type": "bubble",
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "md",
                            "contents": [
                            {
                                "type": "text",
                                "text": f"{ self.activity.title }",
                                "wrap": True,
                                "weight": "bold",
                                "gravity": "center",
                                "size": "xl"
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "margin": "lg",
                                "spacing": "sm",
                                "contents": [
                                {
                                    "type": "box",
                                    "layout": "baseline",
                                    "spacing": "sm",
                                    "contents": [
                                    {
                                        "type": "text",
                                        "text": "ชื่อ",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "text",
                                        "text": f"{ self.first_name } { self.last_name }",
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 4
                                    }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "baseline",
                                    "spacing": "sm",
                                    "contents": [
                                    {
                                        "type": "text",
                                        "text": "เวลา",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "text",
                                        "text": f"{ self.date_updated.strftime('%d/%m/%Y %H:%M') }",
                                        "wrap": True,
                                        "size": "sm",
                                        "color": "#666666",
                                        "flex": 4
                                    }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "baseline",
                                    "spacing": "sm",
                                    "contents": [
                                    {
                                        "type": "text",
                                        "text": "สถานะ",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "text",
                                        "text": "เช็คอินแล้ว",
                                        "wrap": True,
                                        "color": "#17c950",
                                        "size": "sm",
                                        "flex": 4
                                    }
                                    ]
                                }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "margin": "xxl",
                                "contents": [
                                {
                                    "type": "image",
                                    "url": f"{settings.domain_media}/{self.qrcode}",
                                    "aspectMode": "cover",
                                    "size": "4xl",
                                    "margin": "md"
                                },
                                {
                                    "type": "text",
                                    "text": "You can enter the theater by using this code instead of a ticket",
                                    "color": "#aaaaaa",
                                    "wrap": True,
                                    "margin": "xxl",
                                    "size": "xs"
                                }
                                ]
                            }
                            ]
                        }
                        })
            line_bot_api.push_message(social_user.extra_data['sub'], flex_message)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('ticket-detail', kwargs={'pk': self.pk})
    
    def get_absolute_update_url(self):
        return reverse('ticket-update', kwargs={'pk': self.pk})
    