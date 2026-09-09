from django import forms
from .models import Appointment
from apps.doctors.models import DoctorProfile
from apps.facilities.models import Facility

class AppointmentBookingForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['facility', 'doctor', 'scheduled_datetime', 'consultation_type', 'chief_complaint']
        widgets = {
            'facility': forms.Select(attrs={'class': 'form-select'}),
            'doctor': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_datetime': forms.DateTimeInput(attrs={'class': 'form-input', 'type': 'datetime-local'}),
            'consultation_type': forms.Select(attrs={'class': 'form-select'}),
            'chief_complaint': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Describe your symptoms or reason for visit...'}),
        }
