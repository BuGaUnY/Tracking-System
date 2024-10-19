from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ['user', 'status', 'pdpa']

        widgets = {
             'birthday': forms.DateInput(attrs={'type': 'date'}),
             'address': forms.Textarea(attrs={'rows': 5, 'cols': 40}),
             'phone': forms.NumberInput(attrs={'data-mask':'0000000000',}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = True
        self.fields['first_name'].required = True
        self.fields['first_name'].label = "ชื่อจริง"

        self.fields['last_name'].required = True
        self.fields['last_name'].label = "นามสกุล"

        self.fields['birthday'].required = True
        self.fields['birthday'].label = "วันเกิด"

        self.fields['email'].required = True
        self.fields['email'].label = "อีเมล์"

        self.fields['student_number'].label = "รหัสประจำตัว"

        self.fields['degree'].label = "ระดับชั้น"      

        self.fields['room'].label = "ห้อง #รูปแบบการกรอก เช่น A1 B2 C3"
        
        self.fields['department'].label = "แผนก"
        
        self.fields['phone'].required = True
        self.fields['phone'].label = "เบอร์โทรศัพท์"

        self.fields['address'].required = True
        self.fields['address'].label = "ที่อยู่"




