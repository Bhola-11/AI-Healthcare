from django import forms
from .models import Encounter, SOAPNote, EncounterDiagnosis, ICD10DiagnosisCode

class SOAPNoteForm(forms.ModelForm):
    class Meta:
        model = SOAPNote
        fields = ['subjective', 'objective', 'assessment', 'plan']
        widgets = {
            'subjective': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4, 'placeholder': 'Patient history of present illness, symptoms, pain severity, review of systems...'}),
            'objective': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4, 'placeholder': 'Physical examination findings: HEENT, cardiovascular, chest/lungs, abdomen, extremities...'}),
            'assessment': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Primary clinical diagnostic impressions, differential diagnoses...'}),
            'plan': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Therapeutic orders, medications, diagnostic tests, patient advisories, follow-up...'}),
        }

class EncounterDiagnosisForm(forms.ModelForm):
    class Meta:
        model = EncounterDiagnosis
        fields = ['icd10', 'diagnosis_type', 'clinical_notes']
        widgets = {
            'icd10': forms.Select(attrs={'class': 'form-select'}),
            'diagnosis_type': forms.Select(attrs={'class': 'form-select'}),
            'clinical_notes': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Clinical staging or specificity notes'}),
        }
