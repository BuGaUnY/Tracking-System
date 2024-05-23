from django import forms
from .models import Ticket, AttendanceCheckin

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = '__all__'
        exclude = ['activity', 'qrcode', 'profile', 'checkin']
    
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
        fields = '__all__'
        widgets = {
            'date_checkin': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].label = "ชื่อจริง"
        self.fields['last_name'].label = "นามสกุล"
        self.fields['room'].label = "ห้อง"
        self.fields['degree'].label = "ชั้นปี"
        self.fields['department'].label = "แผนก"
