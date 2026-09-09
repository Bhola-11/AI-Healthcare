from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import PatientProfile, VitalSign, Allergy
from .forms import PatientSearchForm, VitalSignForm

@login_required
def patient_list(request):
    form = PatientSearchForm(request.GET)
    patients = PatientProfile.objects.select_related('user').all()
    if form.is_valid():
        q = form.cleaned_data.get('query')
        bg = form.cleaned_data.get('blood_group')
        if q:
            patients = patients.filter(
                Q(mrn__icontains=q) |
                Q(user__first_name__icontains=q) |
                Q(user__last_name__icontains=q) |
                Q(user__email__icontains=q)
            )
        if bg:
            patients = patients.filter(blood_group=bg)
    return render(request, 'patients/list.html', {'patients': patients, 'form': form})

@login_required
def patient_detail(request, patient_id):
    patient = get_object_or_404(PatientProfile, id=patient_id)
    vitals = patient.vital_signs.all()[:10]
    allergies = patient.allergies.filter(is_active=True)
    history = patient.medical_history.all()
    surgeries = patient.surgical_history.all()
    contacts = patient.emergency_contacts.all()
    return render(request, 'patients/detail.html', {
        'patient': patient,
        'vitals': vitals,
        'allergies': allergies,
        'history': history,
        'surgeries': surgeries,
        'contacts': contacts
    })

@login_required
def record_vitals(request, patient_id):
    patient = get_object_or_404(PatientProfile, id=patient_id)
    if request.method == 'POST':
        form = VitalSignForm(request.POST)
        if form.is_valid():
            v = form.save(commit=False)
            v.patient = patient
            v.save()
            messages.success(request, f"Vitals recorded for {patient.user.get_full_name()}.")
            return redirect('patients:detail', patient_id=patient.id)
    else:
        form = VitalSignForm()
    return render(request, 'patients/record_vitals.html', {'patient': patient, 'form': form})
