from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Encounter, SOAPNote, EncounterDiagnosis, ICD10DiagnosisCode, ClinicalAttachment
from .forms import SOAPNoteForm, EncounterDiagnosisForm
from apps.appointments.models import Appointment

@login_required
def encounter_list(request):
    encounters = Encounter.objects.select_related('patient__user', 'doctor__user', 'facility').all()[:50]
    return render(request, 'clinical/encounter_list.html', {'encounters': encounters})

@login_required
def consultation_workspace(request, encounter_id):
    encounter = get_object_or_404(Encounter, id=encounter_id)
    soap_note, _ = SOAPNote.objects.get_or_create(encounter=encounter)
    diagnoses = encounter.diagnoses.select_related('icd10').all()
    attachments = encounter.attachments.all()
    past_encounters = Encounter.objects.filter(patient=encounter.patient).exclude(id=encounter.id)[:5]
    
    if request.method == 'POST':
        form = SOAPNoteForm(request.POST, instance=soap_note)
        if form.is_valid():
            note = form.save(commit=False)
            if 'sign_note' in request.POST:
                note.sign_note()
                encounter.status = Encounter.EncounterStatus.FINISHED
                encounter.end_time = timezone.now()
                encounter.save()
                messages.success(request, f"Clinical SOAP note for Encounter #{encounter.encounter_number} signed and finalized.")
            else:
                note.save()
                messages.info(request, "Consultation draft autosaved.")
            return redirect('clinical_records:consultation', encounter_id=encounter.id)
    else:
        form = SOAPNoteForm(instance=soap_note)
        
    diag_form = EncounterDiagnosisForm()
    return render(request, 'clinical/workspace.html', {
        'encounter': encounter,
        'soap_note': soap_note,
        'form': form,
        'diag_form': diag_form,
        'diagnoses': diagnoses,
        'attachments': attachments,
        'past_encounters': past_encounters
    })

@login_required
def add_diagnosis(request, encounter_id):
    encounter = get_object_or_404(Encounter, id=encounter_id)
    if request.method == 'POST':
        form = EncounterDiagnosisForm(request.POST)
        if form.is_valid():
            d = form.save(commit=False)
            d.encounter = encounter
            d.save()
            messages.success(request, f"Diagnosis {d.icd10.code} added.")
    return redirect('clinical_records:consultation', encounter_id=encounter.id)
