from django.db import models
from django.contrib.auth.models import User
from projectmanager import settings
from allauth.socialaccount.models import SocialAccount
from linebot import LineBotApi
from linebot.models import *
import uuid
from linebot.models import FlexSendMessage

# Create your models here.
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
    ('ช่างเชื่อมโลหะ/เทคนิคโลหะ ', 'ช่างเชื่อมโลหะ/เทคนิคโลหะ'),
    ('ช่างอิเล็กทรอนิกส์', 'ช่างอิเล็กทรอนิกส์'),
    ('สถาปัตยกรรม', 'สถาปัตยกรรม'),
    ('ช่างโยธา', 'ช่างอิเล็กทรอนิกส์'),
    ('ช่างอิเล็กทรอนิกส์', 'ช่างโยธา'),
    ('เทคโนโลยีสารสนเทศ', 'เทคโนโลยีสารสนเทศ'),
    ('การบัญชี', 'การบัญชี'),
    ('การตลาด', 'การตลาด'),
    ('คอมพิวเตอร์ธุรกิจ', 'คอมพิวเตอร์ธุรกิจ'),
    ('การเลขานุการ ', 'การเลขานุการ '),
    ('การจัดการ', 'การจัดการ'),
    )

    # PREFIX_CHOICES = (
    #     ('นาย', 'นาย'),
    #     ('นางสาว', 'นางสาว'),
    #     ('นาง', 'นาง'), 
    # )

    uid = models.UUIDField(default = uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile-image', null=True, blank=True, default='profile-image/default.png')
    # prefix = models.CharField(max_length=200, null=True, blank=True, choices=PREFIX_CHOICES)
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
    
    def __str__(self):
        return self.first_name
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_status = self.status
    
    def save(self, *args, **kwargs):
        # Check image None
        if self.image == '':
            self.image = "profile-image/default.png"
        social_user = SocialAccount.objects.get(user=self.user)
        if self.status == True and self.__original_status == False:
            flex_message = FlexSendMessage(
                alt_text='ยืนยันตัวตน',
                contents={
                            "type": "bubble",
                            "hero": {
                                "type": "image",
                                "url": f"{settings.domain_media}/{self.image}",
                                "size": "full",
                                "aspectRatio": "20:13",
                                "aspectMode": "cover",
                                "action": {
                                "type": "uri",
                                "uri": "http://linecorp.com/"
                                }
                            },
                            "body": {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                {
                                    "type": "text",
                                    "text": "การยืนยันตัวตน",
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
                                        "spacing": "sm",
                                        "contents": [
                                        {
                                            "type": "text",
                                            "text": "สถานะ",
                                            "size": "sm",
                                            "flex": 1
                                        },
                                        {
                                            "type": "text",
                                            "text": "ผ่านการตรวจสอบแล้ว",
                                            "wrap": True,
                                            "color": "#17c950",
                                            "size": "sm",
                                            "flex": 5
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
                                            "size": "sm",
                                            "flex": 1
                                        },
                                        {
                                            "type": "text",
                                            "text": f"{self.date_updated.strftime('%d/%m/%Y %H:%M')}",
                                            "wrap": True,
                                            "size": "sm",
                                            "flex": 5
                                        }
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "baseline",
                                        "contents": [
                                        {
                                            "type": "text",
                                            "text": "ชื่อ",
                                            "size": "sm",
                                            "flex": 1
                                        },
                                        {
                                            "type": "text",
                                            "text": f"{self.first_name} {self.last_name}",
                                            "wrap": True,
                                            "size": "sm",
                                            "flex": 5
                                        }
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "baseline",
                                        "contents": [
                                        {
                                            "type": "text",
                                            "text": "เบอร์โทร",
                                            "size": "sm",
                                            "flex": 2
                                        },
                                        {
                                            "type": "text",
                                            "text": f"{ self.phone }",
                                            "wrap": True,
                                            "size": "sm",
                                            "flex": 5
                                        }
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
                                    "uri": "https://liff.line.me/1656180859-N3MpgwlE/profile"
                                    }
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [],
                                    "margin": "sm"
                                }
                                ],
                                "flex": 0
                            }
                            }
            )
            line_bot_api.push_message(social_user.extra_data['sub'], flex_message)
        super().save(*args, **kwargs)

