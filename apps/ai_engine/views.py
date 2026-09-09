from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ClinicalTriageAssessment, DrugInteractionRule, ClinicalRiskScoreLog
from .services import TriageEngineService, DrugSafetyEngineService, DiagnosticSuggestionService
from apps.patients.models import PatientProfile

@login_required
def triage_view(request):
    patients = PatientProfile.objects.select_related('user').all()
    recent = ClinicalTriageAssessment.objects.select_related('patient__user').all()[:20]
    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        complaint = request.POST.get('complaint', '')
        pain_score = int(request.POST.get('pain_score', 0))
        flag = request.POST.get('red_flag')
        
        patient = get_object_or_404(PatientProfile, id=patient_id)
        flags = [flag] if flag else []
        vitals = patient.vital_signs.first()
        
        assessment = TriageEngineService.evaluate(
            patient=patient,
            complaint=complaint,
            vitals=vitals,
            pain_score=pain_score,
            flags=flags
        )
        messages.success(request, f"Triage completed: {assessment.get_urgency_level_display()} -> {assessment.recommended_disposition}")
        return redirect('ai_engine:triage')
        
    return render(request, 'ai_engine/triage.html', {'patients': patients, 'recent': recent})
