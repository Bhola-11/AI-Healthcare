from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Medication, BatchInventory, DispensationRecord
from apps.prescriptions.models import Prescription, PrescriptionItem

@login_required
def pharmacy_inventory(request):
    medications = Medication.objects.filter(is_active=True).prefetch_related('batches')
    return render(request, 'pharmacy/inventory.html', {'medications': medications})

@login_required
def dispensing_workbench(request):
    pending_rx = Prescription.objects.filter(status=Prescription.Status.SIGNED).select_related('patient__user', 'doctor__user').prefetch_related('items')
    return render(request, 'pharmacy/workbench.html', {'prescriptions': pending_rx})

@login_required
def dispense_rx(request, rx_id):
    rx = get_object_or_404(Prescription, id=rx_id)
    if request.method == 'POST':
        # Allocate batches and deduct inventory
        for item in rx.items.all():
            med = Medication.objects.filter(brand_name__icontains=item.medication_name.split()[0]).first()
            if med:
                batch = med.batches.filter(quantity_on_hand__gte=item.quantity, expiry_date__gt=timezone.now().date()).first()
                if batch:
                    batch.quantity_on_hand -= item.quantity
                    batch.save()
                    DispensationRecord.objects.create(
                        batch=batch,
                        rx_item_id=item.id,
                        quantity_dispensed=item.quantity,
                        dispensed_by=request.user.get_full_name()
                    )
        rx.status = Prescription.Status.DISPENSED
        rx.save()
        messages.success(request, f"Prescription #{rx.rx_number} successfully dispensed and inventory updated.")
        return redirect('pharmacy:workbench')
    return render(request, 'pharmacy/dispense_confirm.html', {'rx': rx})
