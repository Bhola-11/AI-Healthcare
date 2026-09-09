from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Prescription, PrescriptionItem
from .forms import PrescriptionForm, PrescriptionItemForm
from apps.doctors.models import DoctorProfile

@login_required
def prescription_list(request):
    if hasattr(request.user, 'doctor_profile'):
        prescriptions = Prescription.objects.filter(doctor=request.user.doctor_profile).select_related('patient__user')
    elif hasattr(request.user, 'patient_profile'):
        prescriptions = Prescription.objects.filter(patient=request.user.patient_profile).select_related('doctor__user')
    else:
        prescriptions = Prescription.objects.select_related('patient__user', 'doctor__user').all()[:50]
    return render(request, 'prescriptions/list.html', {'prescriptions': prescriptions})

@login_required
def prescription_create(request):
    if not hasattr(request.user, 'doctor_profile'):
        messages.error(request, "Only licensed physicians can issue digital prescriptions.")
        return redirect('prescriptions:list')
        
    doctor = request.user.doctor_profile
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        item_form = PrescriptionItemForm(request.POST)
        if form.is_valid() and item_form.is_valid():
            rx_num = f"RX-{int(timezone.now().timestamp())}"
            rx = form.save(commit=False)
            rx.rx_number = rx_num
            rx.doctor = doctor
            rx.save()
            
            item = item_form.save(commit=False)
            item.prescription = rx
            item.save()
            
            messages.success(request, f"Prescription #{rx.rx_number} successfully issued and digitally signed.")
            return redirect('prescriptions:detail', rx_id=rx.id)
    else:
        initial_expire = (timezone.now() + timedelta(days=90)).date()
        form = PrescriptionForm(initial={'expires_at': initial_expire})
        item_form = PrescriptionItemForm()
    return render(request, 'prescriptions/create.html', {'form': form, 'item_form': item_form})

@login_required
def prescription_detail(request, rx_id):
    rx = get_object_or_404(Prescription, id=rx_id)
    items = rx.items.all()
    return render(request, 'prescriptions/detail.html', {'rx': rx, 'items': items})
