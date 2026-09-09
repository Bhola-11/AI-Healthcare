import uuid
from decimal import Decimal
from django.db import models
from django.utils import timezone
from apps.patients.models import PatientProfile
from apps.clinical_records.models import Encounter


class FeeSchedule(models.Model):
    class ServiceCategory(models.TextChoices):
        CONSULTATION = "CONSULTATION", "Physician Consultation"
        DIAGNOSTIC_LAB = "DIAGNOSTIC_LAB", "Clinical Laboratory Test"
        RADIOLOGY = "RADIOLOGY", "Radiology / Diagnostic Imaging"
        SURGICAL_PROCEDURE = "SURGICAL_PROCEDURE", "Surgical / Minor Procedure"
        ROOM_BOARD = "ROOM_BOARD", "Inpatient Room & Bed Accommodation"
        PHARMACY = "PHARMACY", "Medication & Biological Supplies"
        EMERGENCY_FEE = "EMERGENCY_FEE", "Emergency Resuscitation & Triage Fee"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=32, unique=True, db_index=True)
    description = models.CharField(max_length=255)
    category = models.CharField(max_length=32, choices=ServiceCategory.choices, default=ServiceCategory.CONSULTATION)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    tax_rate_percent = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "hs_billing_fee_schedules"
        ordering = ["category", "code"]

    def __str__(self):
        return f"{self.code} - {self.description} (${self.base_price})"
