from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import HospitalKPIReport
from apps.facilities.models import Facility, Bed
from apps.appointments.models import Appointment
from apps.patients.models import PatientProfile
from apps.billing.models import Invoice

@login_required
def analytics_kpis(request):
    total_patients = PatientProfile.objects.count()
    total_beds = Bed.objects.count()
    occupied_beds = Bed.objects.filter(status=Bed.Status.OCCUPIED).count()
    occ_rate = round((occupied_beds / total_beds * 100), 1) if total_beds > 0 else 0.0
    
    total_invoiced = sum(inv.total_amount for inv in Invoice.objects.all()) or 0
    total_collected = sum(inv.amount_paid for inv in Invoice.objects.all()) or 0
    
    return render(request, 'analytics/kpis.html', {
        'total_patients': total_patients,
        'total_beds': total_beds,
        'occupied_beds': occupied_beds,
        'occ_rate': occ_rate,
        'total_invoiced': total_invoiced,
        'total_collected': total_collected
    })
