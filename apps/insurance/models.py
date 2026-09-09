import uuid
from decimal import Decimal
from django.db import models
from django.utils import timezone
from apps.patients.models import PatientProfile


class InsuranceProvider(models.Model):
    class PayorType(models.TextChoices):
        COMMERCIAL = "COMMERCIAL", "Commercial Private Insurer"
        MEDICARE = "MEDICARE", "Federal Medicare (Part A/B/C/D)"
        MEDICAID = "MEDICAID", "State Medicaid Program"
        TRICARE = "TRICARE", "Military & Veteran Health"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, db_index=True)
    payor_id = models.CharField(max_length=32, unique=True, db_index=True)
    payor_type = models.CharField(max_length=32, choices=PayorType.choices, default=PayorType.COMMERCIAL)
    claims_email = models.EmailField()
    claims_phone = models.CharField(max_length=32)
    address = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "hs_insurance_providers"

    def __str__(self):
        return f"{self.name} [{self.payor_id}]"


class PatientInsurancePolicy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="insurance_policies")
    provider = models.ForeignKey(InsuranceProvider, on_delete=models.CASCADE, related_name="policies")
    policy_number = models.CharField(max_length=64, db_index=True)
    group_number = models.CharField(max_length=64, blank=True)
    copay_amount = models.DecimalField(max_digits=10, decimal_places=2, default=25.00)
    coinsurance_percent = models.DecimalField(max_digits=4, decimal_places=2, default=20.00)
    annual_deductible = models.DecimalField(max_digits=10, decimal_places=2, default=1500.00)
    coverage_limit = models.DecimalField(max_digits=12, decimal_places=2, default=1000000.00)
    effective_start_date = models.DateField()
    effective_end_date = models.DateField()
    is_primary = models.BooleanField(default=True)

    class Meta:
        db_table = "hs_patient_insurance_policies"

    def __str__(self):
        return f"{self.provider.name} Policy #{self.policy_number} for {self.patient}"
