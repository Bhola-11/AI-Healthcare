import uuid
from django.db import models
from django.utils import timezone


class Medication(models.Model):
    class Form(models.TextChoices):
        TABLET = "TABLET", "Tablet"
        CAPSULE = "CAPSULE", "Capsule"
        SYRUP = "SYRUP", "Oral Liquid / Syrup"
        INJECTION = "INJECTION", "Injectable Solution"
        OINTMENT = "OINTMENT", "Topical Ointment / Cream"
        INHALER = "INHALER", "Metered Dose Inhaler"
        SUPPOSITORY = "SUPPOSITORY", "Suppository"
        DROPS = "DROPS", "Ophthalmic / Otic Drops"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand_name = models.CharField(max_length=255, db_index=True)
    generic_name = models.CharField(max_length=255, db_index=True)
    atc_code = models.CharField(max_length=16, db_index=True, help_text="WHO Anatomical Therapeutic Chemical code")
    drug_class = models.CharField(max_length=128)
    dosage_form = models.CharField(max_length=32, choices=Form.choices, default=Form.TABLET)
    strength = models.CharField(max_length=64, help_text="e.g. 500mg, 10mg/ml")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=10.00)
    is_controlled = models.BooleanField(default=False)
    is_antibiotic = models.BooleanField(default=False)
    requires_refrigeration = models.BooleanField(default=False)
    black_box_warning = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "hs_pharmacy_medications"
        ordering = ["generic_name", "brand_name"]

    def __str__(self):
        return f"{self.brand_name} ({self.generic_name}) {self.strength} - {self.dosage_form}"

class BatchInventory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name="batches")
    batch_number = models.CharField(max_length=64, db_index=True)
    lot_number = models.CharField(max_length=64, blank=True)
    manufacturing_date = models.DateField()
    expiry_date = models.DateField(db_index=True)
    quantity_received = models.PositiveIntegerField()
    quantity_on_hand = models.PositiveIntegerField()
    reorder_level = models.PositiveIntegerField(default=50)
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=5.00)
    is_quarantined = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "hs_pharmacy_batches"
        unique_together = ("medication", "batch_number")
        ordering = ["expiry_date"]

    @property
    def is_expired(self):
        return self.expiry_date < timezone.now().date()

    @property
    def is_low_stock(self):
        return self.quantity_on_hand <= self.reorder_level

    def __str__(self):
        return f"{self.medication.brand_name} Lot:{self.batch_number} (Qty: {self.quantity_on_hand}, Exp: {self.expiry_date})"

class DispensationRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch = models.ForeignKey(BatchInventory, on_delete=models.CASCADE, related_name="dispensations")
    rx_item_id = models.UUIDField(null=True, blank=True)
    quantity_dispensed = models.PositiveIntegerField()
    dispensed_by = models.CharField(max_length=255, default="Staff Pharmacist")
    dispensed_at = models.DateTimeField(default=timezone.now)
    patient_counseling_completed = models.BooleanField(default=True)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "hs_pharmacy_dispensations"
