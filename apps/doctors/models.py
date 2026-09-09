import uuid
from django.db import models
from django.utils import timezone
from apps.accounts.models import User
from apps.facilities.models import Facility


class DoctorProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="doctor_profile")
    npi_number = models.CharField(max_length=10, unique=True, db_index=True)
    license_number = models.CharField(max_length=64, unique=True)
    licensing_state = models.CharField(max_length=64, default="New York")
    license_expiry_date = models.DateField()
    years_of_experience = models.PositiveIntegerField(default=5)
    default_consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=150.00)
    biography = models.TextField(blank=True)
    is_telehealth_enabled = models.BooleanField(default=True)
    is_accepting_new_patients = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hs_doctor_profiles"
        ordering = ["user__last_name"]

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} (NPI: {self.npi_number})"

class Specialty(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, unique=True)
    code = models.CharField(max_length=32, unique=True)
    description = models.TextField(blank=True)
    board_name = models.CharField(max_length=255, default="American Board of Medical Specialties")

    class Meta:
        db_table = "hs_medical_specialties"
        verbose_name_plural = "Specialties"
        ordering = ["name"]

    def __str__(self):
        return self.name


class DoctorSpecialty(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name="specialties")
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, related_name="doctors")
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = "hs_doctor_specialty_mappings"
        unique_together = ("doctor", "specialty")


class DoctorQualification(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name="qualifications")
    degree_name = models.CharField(max_length=128)
    institution = models.CharField(max_length=255)
    graduation_year = models.PositiveIntegerField()

    class Meta:
        db_table = "hs_doctor_qualifications"

class DoctorSchedule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name="schedules")
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name="doctor_schedules")
    day_of_week = models.IntegerField(choices=[
        (0, "Monday"), (1, "Tuesday"), (2, "Wednesday"), (3, "Thursday"),
        (4, "Friday"), (5, "Saturday"), (6, "Sunday")
    ])
    start_time = models.TimeField(default="09:00:00")
    end_time = models.TimeField(default="17:00:00")
    slot_duration_minutes = models.PositiveIntegerField(default=30)
    max_patients_per_slot = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "hs_doctor_schedules"
        unique_together = ("doctor", "facility", "day_of_week")

    def __str__(self):
        return f"{self.doctor} - {self.get_day_of_week_display()} ({self.start_time}-{self.end_time})"
