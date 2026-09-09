from django import forms
from .models import PatientProfile, VitalSign, Allergy

class PatientSearchForm(forms.Form):
    query = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Search by MRN, Name, or Email...'}))
    blood_group = forms.ChoiceField(choices=[("", "All Blood Groups")] + PatientProfile.BloodGroup.choices, required=False, widget=forms.Select(attrs={'class': 'form-select'}))

class VitalSignForm(forms.ModelForm):
    class Meta:
        model = VitalSign
        fields = ['systolic_bp', 'diastolic_bp', 'heart_rate', 'respiratory_rate', 'temperature_celsius', 'spo2_percentage', 'weight_kg', 'height_cm', 'notes']
        widgets = {
            'systolic_bp': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '120'}),
            'diastolic_bp': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '80'}),
            'heart_rate': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '72'}),
            'respiratory_rate': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '16'}),
            'temperature_celsius': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '37.0'}),
            'spo2_percentage': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '98'}),
            'weight_kg': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '70.5'}),
            'height_cm': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '175'}),
            'notes': forms.TextInput(attrs={'class': 'form-input'}),
        }
