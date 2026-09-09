import uuid
from django.db import models
from django.utils import timezone
from apps.patients.models import PatientProfile
from apps.doctors.models import DoctorProfile
from apps.facilities.models import Facility
from apps.appointments.models import Appointment


class Encounter(models.Model):
    class EncounterClass(models.TextChoices):
        AMBULATORY = "AMBULATORY", "Outpatient Ambulatory Visit"
        EMERGENCY = "EMERGENCY", "Emergency Department Visit"
        INPATIENT = "INPATIENT", "Inpatient Hospital Admission"
        TELEMEDICINE = "TELEMEDICINE", "Virtual Telemedicine Encounter"
        HOME_HEALTH = "HOME_HEALTH", "Home Health Care Visit"

    class EncounterStatus(models.TextChoices):
        PLANNED = "PLANNED", "Planned / Scheduled"
        ARRIVED = "ARRIVED", "Patient Arrived"
        IN_PROGRESS = "IN_PROGRESS", "Clinical Consultation Active"
        ON_HOLD = "ON_HOLD", "On Hold (Pending Diagnostics)"
        FINISHED = "FINISHED", "Encounter Signed & Closed"
        CANCELLED = "CANCELLED", "Encounter Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    encounter_number = models.CharField(max_length=32, unique=True, db_index=True)
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="encounters")
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name="encounters")
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name="encounters")
    appointment = models.OneToOneField(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name="encounter")
    
    encounter_class = models.CharField(max_length=32, choices=EncounterClass.choices, default=EncounterClass.AMBULATORY)
    status = models.CharField(max_length=32, choices=EncounterStatus.choices, default=EncounterStatus.IN_PROGRESS, db_index=True)
    
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    discharge_disposition = models.CharField(max_length=64, blank=True, choices=[
        ("ROUTINE", "Discharged to Home / Routine"),
        ("ADMIT", "Admitted to Inpatient Ward"),
        ("TRANSFER", "Transferred to Tertiary Center"),
        ("AMA", "Left Against Medical Advice"),
        ("EXPIRED", "Patient Expired")
    ])
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hs_clinical_encounters"
        ordering = ["-start_time"]

    def __str__(self):
        return f"Encounter #{self.encounter_number} - {self.patient} with Dr. {self.doctor.user.get_full_name()}"
