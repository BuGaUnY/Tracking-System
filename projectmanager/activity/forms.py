from django import forms
from .models import Ticket, AttendanceCheckin, Attendance
from .models import Profile
from django.forms import inlineformset_factory

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = '__all__'
        exclude = ['activity', 'qrcode', 'profile', 'checkin']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student_number'].label = "รหัสประจำตัว"
        self.fields['first_name'].label = "ชื่อจริง"
        self.fields['last_name'].label = "นามสกุล"
        self.fields['room'].label = "ห้อง"
        self.fields['degree'].label = "ชั้นปี"
        self.fields['department'].label = "แผนก"

class AttendanceCheckinForm(forms.ModelForm):

    PRESENCE_CHOICES = [
        (True, 'Present'),
        (False, 'Absent'),
    ]

    presence = forms.ChoiceField(
        choices=PRESENCE_CHOICES,
        widget=forms.Select
    )

    class Meta:
        model = AttendanceCheckin
        fields = ['student_number', 'first_name', 'last_name', 'room', 'degree', 'department', 'presence']
        widgets = {
            'student_number': forms.HiddenInput(),
            'first_name': forms.HiddenInput(),
            'last_name': forms.HiddenInput(),
            'room': forms.HiddenInput(),
            'degree': forms.HiddenInput(),
            'department': forms.HiddenInput(),
        }

AttendanceCheckinFormSet = inlineformset_factory(
    Attendance,
    AttendanceCheckin,
    form=AttendanceCheckinForm,
    extra=0,  # No extra forms initially
    can_delete=False
)

