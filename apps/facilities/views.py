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
