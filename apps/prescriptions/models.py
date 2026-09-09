import hashlib
import uuid
from django.db import models
from django.utils import timezone
from apps.patients.models import PatientProfile
from apps.doctors.models import DoctorProfile
from apps.clinical_records.models import Encounter


class Prescription(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft Prescription"
        SIGNED = "SIGNED", "Signed & Issued by Physician"
        PARTIALLY_DISPENSED = "PARTIALLY_DISPENSED", "Partially Dispensed"
        DISPENSED = "DISPENSED", "Fully Dispensed by Pharmacy"
        CANCELLED = "CANCELLED", "Cancelled / Discontinued"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rx_number = models.CharField(max_length=32, unique=True, db_index=True)
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="prescriptions")
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name="prescriptions")
    encounter = models.ForeignKey(Encounter, on_delete=models.SET_NULL, null=True, blank=True, related_name="prescriptions")
    
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.SIGNED, db_index=True)
    signature_hash = models.CharField(max_length=64, blank=True)
    prescribed_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateField()
    clinical_instructions = models.TextField(blank=True)
    is_controlled_substance = models.BooleanField(default=False)

    class Meta:
        db_table = "hs_prescriptions"
        ordering = ["-prescribed_at"]

    def generate_signature(self):
        payload = f"RX:{self.rx_number}:{self.doctor.id}:{self.patient.id}:{self.prescribed_at.isoformat()}"
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

    def save(self, *args, **kwargs):
        if not self.signature_hash:
            self.signature_hash = self.generate_signature()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Rx #{self.rx_number} for {self.patient.user.get_full_name()} by Dr. {self.doctor.user.get_full_name()}"
