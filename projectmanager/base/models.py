from django.db import models
from django.contrib.auth.models import User
from projectmanager import settings
from allauth.socialaccount.models import SocialAccount
from linebot import LineBotApi
from linebot.models import *
import uuid
from linebot.models import FlexSendMessage

# Create your models here.
# line_bot_api = LineBotApi(settings.channel_access_token)

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
    ('ช่างเชื่อมโลหะ/เทคนิคโลหะ ', 'ช่างเชื่อมโลหะ/เทคนิคโลหะ'),
    ('ช่างอิเล็กทรอนิกส์', 'ช่างอิเล็กทรอนิกส์'),
    ('สถาปัตยกรรม', 'สถาปัตยกรรม'),
    ('ช่างโยธา', 'ช่างโยธา'),
    ('เทคโนโลยีสารสนเทศ', 'เทคโนโลยีสารสนเทศ'),
    ('การบัญชี', 'การบัญชี'),
    ('การตลาด', 'การตลาด'),
    ('คอมพิวเตอร์ธุรกิจ', 'คอมพิวเตอร์ธุรกิจ'),
    ('การเลขานุการ ', 'การเลขานุการ '),
    ('การจัดการ', 'การจัดการ'),
    )

    # GENDER_CHOICES = (
    #     ('นาย', 'นาย'),
    #     ('นางสาว', 'นางสาว'),
    #     ('นาง', 'นาง'), 
    # )

    uid = models.UUIDField(default = uuid.uuid4, editable=False, unique=True)
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
    date_create = models.DateTimeField(auto_now_add=True, blank=False)
    date_updated = models.DateTimeField(auto_now=True, blank=False)
    

    def __str__(self):
        # ตรวจสอบให้แน่ใจว่าคืนค่าเป็นสตริง
        return f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else "Profile"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_status = self.status
    