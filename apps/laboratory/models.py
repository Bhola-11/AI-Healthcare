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

class DemographicReferenceRange(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    test = models.ForeignKey(LabTestCatalog, on_delete=models.CASCADE, related_name="reference_ranges")
    gender = models.CharField(max_length=16, choices=[("ALL", "All Genders"), ("MALE", "Male"), ("FEMALE", "Female")], default="ALL")
    min_age_years = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
    max_age_years = models.DecimalField(max_digits=4, decimal_places=1, default=120.0)
    
    normal_min = models.DecimalField(max_digits=10, decimal_places=3)
    normal_max = models.DecimalField(max_digits=10, decimal_places=3)
    critical_low = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    critical_high = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)

    class Meta:
        db_table = "hs_lab_reference_ranges"

    def __str__(self):
        return f"{self.test.test_name} Range ({self.gender}, {self.min_age_years}-{self.max_age_years}y): {self.normal_min} - {self.normal_max} {self.test.measurement_unit}"

class LabOrder(models.Model):
    class OrderPriority(models.TextChoices):
        ROUTINE = "ROUTINE", "Routine Outpatient"
        URGENT = "URGENT", "Urgent Clinical Priority"
        STAT = "STAT", "Emergency STAT Immediate"

    class OrderStatus(models.TextChoices):
        PLACED = "PLACED", "Order Placed"
        COLLECTED = "COLLECTED", "Specimen Collected"
        PROCESSING = "PROCESSING", "In Analyzer Processing"
        COMPLETED = "COMPLETED", "Verified & Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=32, unique=True, db_index=True)
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="lab_orders")
    ordering_doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name="lab_orders")
    encounter = models.ForeignKey(Encounter, on_delete=models.SET_NULL, null=True, blank=True, related_name="lab_orders")
    priority = models.CharField(max_length=16, choices=OrderPriority.choices, default=OrderPriority.ROUTINE)
    status = models.CharField(max_length=32, choices=OrderStatus.choices, default=OrderStatus.PLACED, db_index=True)
    clinical_indication = models.TextField(blank=True)
    ordered_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "hs_lab_orders"
        ordering = ["-ordered_at"]

    def __str__(self):
        return f"LabOrder #{self.order_number} for {self.patient} ({self.status})"
