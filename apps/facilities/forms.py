from django import forms
from .models import Facility, Department, Ward, Room, Bed

class FacilityForm(forms.ModelForm):
    class Meta:
        model = Facility
        fields = [
            'name', 'facility_code', 'facility_type', 'license_number',
            'phone', 'email', 'address_line_1', 'city', 'state', 'postal_code',
            'emergency_services_available', 'trauma_level', 'total_capacity'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'facility_code': forms.TextInput(attrs={'class': 'form-input'}),
            'facility_type': forms.Select(attrs={'class': 'form-select'}),
            'license_number': forms.TextInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'address_line_1': forms.TextInput(attrs={'class': 'form-input'}),
            'city': forms.TextInput(attrs={'class': 'form-input'}),
            'state': forms.TextInput(attrs={'class': 'form-input'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-input'}),
            'trauma_level': forms.Select(attrs={'class': 'form-select'}),
            'total_capacity': forms.NumberInput(attrs={'class': 'form-input'}),
        }
