import uuid
from django.db import models
from django.utils import timezone


class Facility(models.Model):
    class FacilityType(models.TextChoices):
        GENERAL_HOSPITAL = "GENERAL_HOSPITAL", "Tertiary General Hospital"
        SPECIALTY_CLINIC = "SPECIALTY_CLINIC", "Specialty Medical Clinic"
        AMBULATORY_CENTER = "AMBULATORY_CENTER", "Ambulatory Surgery Center"
        URGENT_CARE = "URGENT_CARE", "Urgent Care Facility"
        DIAGNOSTIC_LAB = "DIAGNOSTIC_LAB", "Diagnostic & Pathology Center"
        COMMUNITY_HEALTH = "COMMUNITY_HEALTH", "Community Health Clinic"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, db_index=True)
    facility_code = models.CharField(max_length=32, unique=True, db_index=True)
    facility_type = models.CharField(max_length=32, choices=FacilityType.choices, default=FacilityType.GENERAL_HOSPITAL)
    license_number = models.CharField(max_length=128, unique=True)
    accreditation_body = models.CharField(max_length=128, default="Joint Commission / State DOH")
    tax_id = models.CharField(max_length=64, blank=True)
    npi_number = models.CharField(max_length=32, blank=True)
    
    phone = models.CharField(max_length=32)
    email = models.EmailField()
    website = models.URLField(blank=True)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="United States")
    
    is_active = models.BooleanField(default=True)
    emergency_services_available = models.BooleanField(default=True)
    trauma_level = models.CharField(max_length=32, choices=[
        ("LEVEL_1", "Level I Trauma"),
        ("LEVEL_2", "Level II Trauma"),
        ("LEVEL_3", "Level III Trauma"),
        ("NONE", "Non-Trauma Facility")
    ], default="LEVEL_1")
    
    total_capacity = models.PositiveIntegerField(default=100)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hs_facilities"
        verbose_name = "Healthcare Facility"
        verbose_name_plural = "Healthcare Facilities"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.facility_code}) - {self.get_facility_type_display()}"
