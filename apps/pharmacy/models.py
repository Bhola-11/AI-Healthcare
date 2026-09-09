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
