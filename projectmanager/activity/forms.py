from django import forms
from .models import Ticket, AttendanceCheckin

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = '__all__'
        exclude = ['activity', 'qrcode', 'status', 'profile', 'checkin']
        widgets = {
            'phone': forms.NumberInput(attrs={'data-mask':'0000000000'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].label = "ชื่อจริง"
        self.fields['last_name'].label = "นามสกุล"
        self.fields['room'].label = "ห้อง"
        self.fields['degree'].label = "ชั้นปี"
        self.fields['department'].label = "แผนก"


class AttendanceCheckinForm(forms.ModelForm):
    class Meta:
        model = AttendanceCheckin
        fields = ['user','student_number','first_name','last_name', 'room', 'degree', 'department', 'att_name', 'date_checkin', 'presence']
        widgets = {
            'date_checkin': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }


    def clean_presence(self):
        presence = self.cleaned_data['presence']
        if presence not in [0, 1]:
            raise forms.ValidationError("Presence must be either 0 or 1.")
        return presence