from django import forms
from .models import Prescription, PrescriptionItem
from apps.patients.models import PatientProfile

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['patient', 'clinical_instructions', 'expires_at', 'is_controlled_substance']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'clinical_instructions': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
            'expires_at': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }

class PrescriptionItemForm(forms.ModelForm):
    class Meta:
        model = PrescriptionItem
        fields = ['medication_name', 'dosage', 'route', 'frequency', 'duration_days', 'quantity', 'special_instructions']
        widgets = {
            'medication_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Amoxicillin / Clavulanate'}),
            'dosage': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 875/125 mg'}),
            'route': forms.Select(attrs={'class': 'form-select'}),
            'frequency': forms.Select(attrs={'class': 'form-select'}),
            'duration_days': forms.NumberInput(attrs={'class': 'form-input'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-input'}),
            'special_instructions': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Take with meals'}),
        }
