from django.db import models
from django.contrib.auth.models import User
from projectmanager import settings
from allauth.socialaccount.models import SocialAccount
from linebot import LineBotApi
from linebot.models import FlexSendMessage, TextSendMessage
from linebot.exceptions import LineBotApiError
import uuid
import logging
from django.urls import reverse

# Create your models here.
logger = logging.getLogger(__name__)
line_bot_api = LineBotApi(settings.channel_access_token)

class Profile(models.Model):
    DEGREE_CHOICES = (
        ('ปวช.1', 'ปวช.1'),
        ('ปวช.2', 'ปวช.2'),
        ('ปวช.3', 'ปวช.3'),
        ('ปวส.1', 'ปวส.1'),
        ('ปวส.2', 'ปวส.2'),
    )

    DEPARTMENT_CHOICES = (
        ('ช่างยนต์', 'ช่างยนต์'),
        ('ช่างกลโรงงาน', 'ช่างกลโรงงาน'),
        ('ช่างไฟฟ้ากำลัง', 'ช่างไฟฟ้ากำลัง'),
        ('ช่างเทคนิคพลังงาน', 'ช่างเทคนิคพลังงาน'),
        ('ช่างเชื่อมโลหะ/ซ่อมบำรุง', 'ช่างเชื่อมโลหะ/ซ่อมบำรุง'),
        ('ช่างเมคคาทรอนิกส์', 'ช่างเมคคาทรอนิกส์'),
        ('ช่างอิเล็กทรอนิกส์', 'ช่างอิเล็กทรอนิกส์'),
        ('ช่างสถาปัตยกรรม', 'ช่างสถาปัตยกรรม'),
        ('ช่างโยธา', 'ช่างโยธา'),
        ('ช่างก่อสร้าง', 'ช่างก่อสร้าง'),
        ('เทคโนโลยีธุรกิจดิจิทัล', 'เทคโนโลยีธุรกิจดิจิทัล'),
        ('เทคโนโลยีสารสนเทศ', 'เทคโนโลยีสารสนเทศ'),
        ('การบัญชี', 'การบัญชี'),
        ('การตลาด', 'การตลาด'),
    )

    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile-image', null=True, blank=True, default='profile-image/default.png')
    first_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200, null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    student_number = models.CharField(max_length=20, null=True, blank=True)
    degree = models.CharField(max_length=10, null=True, blank=True, choices=DEGREE_CHOICES)
    room = models.CharField(max_length=10, null=True, blank=True)
    department = models.CharField(max_length=50, null=True, blank=True, choices=DEPARTMENT_CHOICES)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=False)
    pdpa = models.BooleanField(default=False)
    date_create = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.room} {self.department} {self.first_name} {self.last_name}"
        return self.first_name or "โปรไฟล์ใหม่"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_status = self.status
    
    def save(self, *args, **kwargs):
        # Check if image is not set
        if not self.image:
            self.image = "profile-image/default.png"

        # Get the original instance for comparison
        original_instance = None
        if self.pk:
            original_instance = self.__class__.objects.filter(pk=self.pk).first()

        # Proceed with save to update the object
        super().save(*args, **kwargs)

        # Compare fields for changes
        fields_to_check = ['first_name', 'last_name', 'phone', 'status', 'image', 'room', 'department', 'degree', 'student_number' ]
        changes_detected = False

        if original_instance:
            for field in fields_to_check:
                original_value = getattr(original_instance, field)
                current_value = getattr(self, field)
                if original_value != current_value:
                    changes_detected = True
                    break

        # Send LINE message if changes are detected
        if changes_detected:
            social_user = SocialAccount.objects.get(user=self.user)
            flex_message = FlexSendMessage(
                alt_text='ยืนยันโปรไฟล์',
                contents={
                    "type": "bubble",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "ยืนยันโปรไฟล์",
                                "weight": "bold",
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
                                        "contents": [
                                            {"type": "text", "text": "ชื่อ", "weight": "bold", "size": "sm", "flex": 1},
                                            {"type": "text", "text": f"{self.first_name} {self.last_name}", "wrap": True, "size": "sm", "flex": 5},
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "baseline",
                                        "contents": [
                                            {"type": "text", "text": "รหัสประจำตัว", "weight": "bold", "size": "sm", "flex": 1},
                                            {"type": "text", "text": f"{self.student_number}", "wrap": True, "size": "sm", "flex": 5},
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "baseline",
                                        "contents": [
                                            {"type": "text", "text": "ห้อง", "weight": "bold", "size": "sm", "flex": 1},
                                            {"type": "text", "text": f"{self.room}", "wrap": True, "size": "sm", "flex": 5},
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "baseline",
                                        "contents": [
                                            {"type": "text", "text": "ระดับชั้น", "weight": "bold", "size": "sm", "flex": 1},
                                            {"type": "text", "text": f"{self.degree}", "wrap": True, "size": "sm", "flex": 5},
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "baseline",
                                        "contents": [
                                            {"type": "text", "text": "แผนก", "weight": "bold", "size": "sm", "flex": 1},
                                            {"type": "text", "text": f"{self.department}", "wrap": True, "size": "sm", "flex": 5},
                                        ]
                                    },                                                                                                                                               
                                    {
                                        "type": "box",
                                        "layout": "baseline",
                                        "contents": [
                                            {"type": "text", "text": "สถานะ", "weight": "bold", "size": "sm", "flex": 1},
                                            {"type": "text", "text": "ยืนยันโปรไฟล์แล้ว" if self.status else "ยังไม่ยืนยันโปรไฟล์", "wrap": True, "color": "#17c950" if self.status else "#ff0000", "size": "sm", "flex": 5},
                                        ]
                                    }
                                ]
                            }
                        ]
                    },
                    "footer": {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "button",
                                "style": "primary",
                                "height": "sm",
                                "action": {
                                    "type": "uri",
                                    "label": "ตรวจสอบโปรไฟล์",
                                    "uri": f"https://https://ctc-sats.ngrok.io/profile/verify/{self.pk}/"
                                }
                            }
                        ],
                        "flex": 0
                    }
                }
            )
            line_bot_api.push_message(social_user.extra_data['sub'], flex_message)
