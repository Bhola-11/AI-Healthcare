from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import DoctorProfile, Specialty, DoctorSchedule, DoctorLeave

@login_required
def doctor_directory(request):
    specialty_filter = request.GET.get('specialty')
    doctors = DoctorProfile.objects.filter(user__is_active=True).select_related('user')
    if specialty_filter:
        doctors = doctors.filter(specialties__specialty__code=specialty_filter)
    specialties = Specialty.objects.all()
    return render(request, 'doctors/directory.html', {'doctors': doctors, 'specialties': specialties})

@login_required
def doctor_detail(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, id=doctor_id)
    schedules = doctor.schedules.filter(is_active=True).select_related('facility')
    specialties = doctor.specialties.select_related('specialty')
    return render(request, 'doctors/detail.html', {'doctor': doctor, 'schedules': schedules, 'specialties': specialties})
