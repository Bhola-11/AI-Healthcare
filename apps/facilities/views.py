from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Facility, Department, Ward, Room, Bed
from .forms import FacilityForm

@login_required
def facility_list(request):
    facilities = Facility.objects.filter(is_active=True)
    return render(request, 'facilities/list.html', {'facilities': facilities})

@login_required
def facility_detail(request, facility_id):
    facility = get_object_or_404(Facility, id=facility_id)
    departments = facility.departments.filter(is_active=True)
    return render(request, 'facilities/detail.html', {'facility': facility, 'departments': departments})

@login_required
def facility_create(request):
    if request.method == 'POST':
        form = FacilityForm(request.POST)
        if form.is_valid():
            fac = form.save()
            messages.success(request, f"Facility {fac.name} successfully registered.")
            return redirect('facilities:detail', facility_id=fac.id)
    else:
        form = FacilityForm()
    return render(request, 'facilities/form.html', {'form': form, 'title': 'Register New Healthcare Facility'})

@login_required
def bed_board_view(request, facility_id=None):
    if facility_id:
        facility = get_object_or_404(Facility, id=facility_id)
        beds = Bed.objects.filter(room__ward__department__facility=facility)
    else:
        facility = Facility.objects.first()
        beds = Bed.objects.all()
    
    total = beds.count()
    available = beds.filter(status=Bed.Status.AVAILABLE).count()
    occupied = beds.filter(status=Bed.Status.OCCUPIED).count()
    maintenance = beds.filter(status__in=[Bed.Status.CLEANING, Bed.Status.MAINTENANCE]).count()
    
    return render(request, 'facilities/bed_board.html', {
        'facility': facility,
        'beds': beds,
        'total': total,
        'available': available,
        'occupied': occupied,
        'maintenance': maintenance
    })
