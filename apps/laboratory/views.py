from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import LabOrder, LabResultItem, LabTestCatalog, SpecimenType, LabSpecimen

@login_required
def lab_order_list(request):
    orders = LabOrder.objects.select_related('patient__user', 'ordering_doctor__user').prefetch_related('results').all()[:50]
    return render(request, 'laboratory/order_list.html', {'orders': orders})

@login_required
def lab_order_detail(request, order_id):
    order = get_object_or_404(LabOrder, id=order_id)
    results = order.results.select_related('test').all()
    specimens = order.specimens.select_related('specimen_type').all()
    return render(request, 'laboratory/detail.html', {'order': order, 'results': results, 'specimens': specimens})

@login_required
def pathologist_signoff(request, order_id):
    order = get_object_or_404(LabOrder, id=order_id)
    if request.method == 'POST':
        order.status = LabOrder.OrderStatus.COMPLETED
        order.completed_at = timezone.now()
        order.save()
        
        for res in order.results.all():
            res.verified_by = request.user.get_full_name()
            res.verified_at = timezone.now()
            res.save()
            
        messages.success(request, f"Laboratory diagnostic order #{order.order_number} verified and released by Pathologist.")
        return redirect('laboratory:detail', order_id=order.id)
    return render(request, 'laboratory/signoff_confirm.html', {'order': order})
