import uuid
from django.db import models
from django.utils import timezone
from apps.patients.models import PatientProfile
from apps.doctors.models import DoctorProfile
from apps.facilities.models import Facility


class Appointment(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Confirmed & Scheduled"
        CHECKED_IN = "CHECKED_IN", "Patient Checked In / Waiting Room"
        IN_CONSULTATION = "IN_CONSULTATION", "In Consultation with Doctor"
        COMPLETED = "COMPLETED", "Consultation Completed"
        CANCELLED = "CANCELLED", "Cancelled by Patient or Clinic"
        RESCHEDULED = "RESCHEDULED", "Rescheduled to Another Slot"
        NO_SHOW = "NO_SHOW", "Patient Did Not Attend"

    class ConsultationType(models.TextChoices):
        GENERAL = "GENERAL", "General Outpatient Consultation"
        FOLLOW_UP = "FOLLOW_UP", "Post-Treatment Follow-up"
        TELEHEALTH = "TELEHEALTH", "Virtual Telehealth Video Consultation"
        SPECIALIST = "SPECIALIST", "Specialist Consultation"
        URGENT = "URGENT", "Urgent Walk-in Care"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment_number = models.CharField(max_length=32, unique=True, db_index=True)
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="appointments")
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name="appointments")
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name="appointments")
    scheduled_datetime = models.DateTimeField(db_index=True)
    duration_minutes = models.PositiveIntegerField(default=30)
    consultation_type = models.CharField(max_length=32, choices=ConsultationType.choices, default=ConsultationType.GENERAL)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.SCHEDULED, db_index=True)
    chief_complaint = models.TextField()
    cancellation_reason = models.TextField(blank=True)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hs_appointments"
        ordering = ["-scheduled_datetime"]

    def __str__(self):
        return f"Appt #{self.appointment_number} - {self.patient.user.get_full_name()} with Dr. {self.doctor.user.get_full_name()}"

class QueueTicket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name="queue_ticket")
    token_number = models.CharField(max_length=16, unique=True, db_index=True)
    issued_at = models.DateTimeField(default=timezone.now)
    called_at = models.DateTimeField(null=True, blank=True)
    is_served = models.BooleanField(default=False)

    class Meta:
        db_table = "hs_queue_tickets"

    def __str__(self):
        return f"Token #{self.token_number} - {self.appointment}"
