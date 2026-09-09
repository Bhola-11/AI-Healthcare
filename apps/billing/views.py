from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Invoice, InvoiceItem, Payment, FeeSchedule
from apps.insurance.models import InsuranceClaim

@login_required
def invoice_list(request):
    invoices = Invoice.objects.select_related('patient__user', 'encounter').all()[:50]
    return render(request, 'billing/invoice_list.html', {'invoices': invoices})

@login_required
def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    items = invoice.items.all()
    payments = invoice.payments.all()
    return render(request, 'billing/detail.html', {'invoice': invoice, 'items': items, 'payments': payments})

@login_required
def process_payment(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if request.method == 'POST':
        amount = request.POST.get('amount')
        method = request.POST.get('payment_method', 'CREDIT_CARD')
        if amount:
            Payment.objects.create(
                payment_reference=f"PAY-{int(timezone.now().timestamp())}",
                invoice=invoice,
                amount=amount,
                payment_method=method,
                received_by=request.user.get_full_name()
            )
            messages.success(request, f"Payment of ${amount} applied to Invoice #{invoice.invoice_number}.")
            return redirect('billing:detail', invoice_id=invoice.id)
    return render(request, 'billing/payment_form.html', {'invoice': invoice})
