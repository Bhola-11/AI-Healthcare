from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Appointment
from .forms import AppointmentBookingForm
from .services import AppointmentBookingService

@login_required
def appointment_list(request):
    if hasattr(request.user, 'patient_profile'):
        appointments = Appointment.objects.filter(patient=request.user.patient_profile).select_related('doctor__user', 'facility')
    elif hasattr(request.user, 'doctor_profile'):
        appointments = Appointment.objects.filter(doctor=request.user.doctor_profile).select_related('patient__user', 'facility')
    else:
        appointments = Appointment.objects.select_related('patient__user', 'doctor__user', 'facility').all()[:50]
    return render(request, 'appointments/list.html', {'appointments': appointments})

@login_required
def book_appointment(request):
    if not hasattr(request.user, 'patient_profile'):
        messages.error(request, "Only registered patients can book clinical appointments.")
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST)
        if form.is_valid():
            try:
                appt = AppointmentBookingService.reserve_slot(
                    patient=request.user.patient_profile,
                    doctor=form.cleaned_data['doctor'],
                    facility=form.cleaned_data['facility'],
                    scheduled_datetime=form.cleaned_data['scheduled_datetime'],
                    chief_complaint=form.cleaned_data['chief_complaint'],
                    consultation_type=form.cleaned_data['consultation_type']
                )
                messages.success(request, f"Appointment #{appt.appointment_number} confirmed with Dr. {appt.doctor.user.get_full_name()}!")
                return redirect('appointments:list')
            except ValueError as e:
                form.add_error(None, str(e))
    else:
        form = AppointmentBookingForm()
    return render(request, 'appointments/book.html', {'form': form})

@login_required
def check_in_patient(request, appointment_id):
    appt = get_object_or_404(Appointment, id=appointment_id)
    appt.status = Appointment.Status.CHECKED_IN
    appt.checked_in_at = timezone.now()
    appt.save()
    
    # Generate token Q-101, Q-102 etc.
    count = QueueTicket.objects.filter(issued_at__date=timezone.now().date()).count() + 1
    token_str = f"Q-{count:03d}"
    QueueTicket.objects.create(appointment=appt, token_number=token_str)
    
    messages.success(request, f"Patient {appt.patient.user.get_full_name()} checked in! Token: {token_str}")
    return redirect('appointments:list')

@login_required
def live_queue_board(request):
    today = timezone.now().date()
    waiting_tickets = QueueTicket.objects.filter(
        issued_at__date=today,
        is_served=False
    ).select_related('appointment__patient__user', 'appointment__doctor__user').order_by('issued_at')
    
    avg_wait_minutes = waiting_tickets.count() * 15 # 15 min per consultation
    return render(request, 'appointments/queue_board.html', {
        'tickets': waiting_tickets,
        'count': waiting_tickets.count(),
        'est_wait': avg_wait_minutes
    })

@login_required
def cancel_appointment(request, appointment_id):
    appt = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        reason = request.POST.get('cancellation_reason', 'Cancelled by user')
        appt.status = Appointment.Status.CANCELLED
        appt.cancellation_reason = reason
        appt.save()
        messages.warning(request, f"Appointment #{appt.appointment_number} has been cancelled.")
        return redirect('appointments:list')
    return render(request, 'appointments/cancel.html', {'appointment': appt})
