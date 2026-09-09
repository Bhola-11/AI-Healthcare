from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from .models import Appointment

class AppointmentBookingService:
    @staticmethod
    @transaction.atomic
    def reserve_slot(patient, doctor, facility, scheduled_datetime, chief_complaint, consultation_type=Appointment.ConsultationType.GENERAL):
        # Select for update to prevent concurrent double-booking
        conflict = Appointment.objects.select_for_update().filter(
            doctor=doctor,
            scheduled_datetime=scheduled_datetime,
            status__in=[Appointment.Status.SCHEDULED, Appointment.Status.CHECKED_IN, Appointment.Status.IN_CONSULTATION]
        ).exists()
        
        if conflict:
            raise ValueError("The requested consultation slot is no longer available.")
            
        appt_num = f"APT-{int(timezone.now().timestamp())}-{str(doctor.id)[:4].upper()}"
        
        appointment = Appointment.objects.create(
            appointment_number=appt_num,
            patient=patient,
            doctor=doctor,
            facility=facility,
            scheduled_datetime=scheduled_datetime,
            chief_complaint=chief_complaint,
            consultation_type=consultation_type,
            status=Appointment.Status.SCHEDULED
        )
        return appointment
