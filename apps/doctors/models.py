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
