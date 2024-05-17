from django import forms
from .models import Ticket

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
        self.fields['phone'].label = "เบอร์โทรศัพท์"
        self.fields['slip'].label = "**หลักฐานการชำระเงิน**"