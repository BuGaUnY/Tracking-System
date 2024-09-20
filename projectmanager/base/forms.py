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
        self.fields['image'].required = False
        self.fields['first_name'].required = True
        self.fields['first_name'].label = "ชื่อจริง"
        self.fields['last_name'].required = True
        self.fields['last_name'].label = "นามสกุล"
        self.fields['birthday'].required = True
        self.fields['birthday'].label = "วันเกิด"
        self.fields['email'].required = True
        self.fields['phone'].required = True
        self.fields['phone'].label = "เบอร์โทรศัพท์"
        self.fields['address'].required = False
        self.fields['address'].label = "ที่อยู่"


    # def clean(self):
    #     cleaned_data = super().clean()
    #     image = cleaned_data.get('image')
    #     first_name = cleaned_data.get('first_name')
    #     last_name = cleaned_data.get('last_name')
    #     birthday = cleaned_data.get('birthday')
    #     email = cleaned_data.get('email')
    #     phone = cleaned_data.get('phone')
    #     address = cleaned_data.get('address')
    #     status = cleaned_data.get('status')
    #     pdpa = cleaned_data.get('pdpa')

    #     if not image and not first_name and not last_name and not birthday and not email and not phone and not address and not status and not pdpa:
    #         raise forms.ValidationError('You have to write something!')

