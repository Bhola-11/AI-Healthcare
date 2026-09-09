import uuid
from django.db import models
from django.utils import timezone
from apps.patients.models import PatientProfile
from apps.doctors.models import DoctorProfile
from apps.clinical_records.models import Encounter


class SpecimenType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=32, unique=True)
    container_type = models.CharField(max_length=100, help_text="e.g. Lavender Top (EDTA), Red Top (Serum), Sterile Cup")
    handling_instructions = models.TextField(blank=True)

    class Meta:
        db_table = "hs_lab_specimen_types"

    def __str__(self):
        return f"{self.name} ({self.container_type})"


class LabTestCatalog(models.Model):
    class Category(models.TextChoices):
        HEMATOLOGY = "HEMATOLOGY", "Hematology & Coagulation"
        BIOCHEMISTRY = "BIOCHEMISTRY", "Clinical Biochemistry"
        IMMUNOLOGY = "IMMUNOLOGY", "Immunology & Serology"
        MICROBIOLOGY = "MICROBIOLOGY", "Microbiology & Culture"
        URINALYSIS = "URINALYSIS", "Urinalysis & Body Fluids"
        ENDOCRINOLOGY = "ENDOCRINOLOGY", "Endocrinology & Hormones"
        TOXICOLOGY = "TOXICOLOGY", "Toxicology & Drug Screens"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loinc_code = models.CharField(max_length=32, db_index=True, unique=True)
    test_name = models.CharField(max_length=255, db_index=True)
    category = models.CharField(max_length=32, choices=Category.choices, default=Category.BIOCHEMISTRY)
    specimen_type = models.ForeignKey(SpecimenType, on_delete=models.CASCADE, related_name="tests")
    measurement_unit = models.CharField(max_length=32, help_text="e.g. mg/dL, mmol/L, g/dL, 10^3/uL")
    standard_cost = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    turnaround_time_hours = models.PositiveIntegerField(default=24)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "hs_lab_test_catalog"
        ordering = ["category", "test_name"]

    def __str__(self):
        return f"{self.test_name} [{self.loinc_code}] ({self.measurement_unit})"
