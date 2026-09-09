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

class Department(models.Model):
    class DepartmentCategory(models.TextChoices):
        CLINICAL = "CLINICAL", "Clinical Specialty"
        DIAGNOSTIC = "DIAGNOSTIC", "Diagnostic & Laboratory"
        SURGICAL = "SURGICAL", "Surgery & Operation Theater"
        EMERGENCY = "EMERGENCY", "Emergency & Critical Care"
        ADMINISTRATIVE = "ADMINISTRATIVE", "Administrative & Support"
        PHARMACY = "PHARMACY", "Pharmacy & Therapeutics"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name="departments")
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=32)
    category = models.CharField(max_length=32, choices=DepartmentCategory.choices, default=DepartmentCategory.CLINICAL)
    head_of_department = models.CharField(max_length=255, blank=True)
    contact_extension = models.CharField(max_length=16, blank=True)
    floor_number = models.CharField(max_length=16, default="1")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "hs_facility_departments"
        unique_together = ("facility", "code")
        ordering = ["facility", "name"]

    def __str__(self):
        return f"{self.name} - {self.facility.name} ({self.code})"

class Ward(models.Model):
    class WardType(models.TextChoices):
        ICU = "ICU", "Intensive Care Unit"
        NICU = "NICU", "Neonatal Intensive Care Unit"
        GENERAL_MALE = "GENERAL_MALE", "General Male Ward"
        GENERAL_FEMALE = "GENERAL_FEMALE", "General Female Ward"
        PEDIATRIC = "PEDIATRIC", "Pediatric Ward"
        MATERNITY = "MATERNITY", "Maternity & Labor"
        POST_OP = "POST_OP", "Post-Operative Recovery"
        ISOLATION = "ISOLATION", "Infection Isolation Ward"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="wards")
    name = models.CharField(max_length=100)
    ward_type = models.CharField(max_length=32, choices=WardType.choices, default=WardType.GENERAL_MALE)
    floor = models.CharField(max_length=16, default="2")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "hs_facility_wards"

    def __str__(self):
        return f"{self.name} ({self.get_ward_type_display()}) - {self.department.name}"


class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name="rooms")
    room_number = models.CharField(max_length=32)
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2, default=150.00)
    has_oxygen_supply = models.BooleanField(default=True)
    has_ventilator = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "hs_facility_rooms"
        unique_together = ("ward", "room_number")

    def __str__(self):
        return f"Room {self.room_number} - {self.ward.name}"


class Bed(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available / Clean"
        OCCUPIED = "OCCUPIED", "Patient Occupied"
        CLEANING = "CLEANING", "Housekeeping / Sanitation"
        MAINTENANCE = "MAINTENANCE", "Biomedical Maintenance"
        RESERVED = "RESERVED", "Reserved for Admission"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="beds")
    bed_identifier = models.CharField(max_length=32)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.AVAILABLE, db_index=True)
    is_electric_adjustable = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    last_cleaned_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "hs_facility_beds"
        unique_together = ("room", "bed_identifier")

    def __str__(self):
        return f"Bed {self.bed_identifier} ({self.room.room_number}) - {self.status}"
