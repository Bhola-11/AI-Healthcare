import uuid
from django.db import models
from django.utils import timezone
from apps.accounts.models import User
from apps.accounts.utils import generate_medical_record_number


class PatientProfile(models.Model):
    class BloodGroup(models.TextChoices):
        A_POS = "A+", "A Positive (A+)"
        A_NEG = "A-", "A Negative (A-)"
        B_POS = "B+", "B Positive (B+)"
        B_NEG = "B-", "B Negative (B-)"
        AB_POS = "AB+", "AB Positive (AB+)"
        AB_NEG = "AB-", "AB Negative (AB-)"
        O_POS = "O+", "O Positive (O+)"
        O_NEG = "O-", "O Negative (O-)"
        UNKNOWN = "UNK", "Unknown"

    class MaritalStatus(models.TextChoices):
        SINGLE = "SINGLE", "Single"
        MARRIED = "MARRIED", "Married"
        DIVORCED = "DIVORCED", "Divorced"
        WIDOWED = "WIDOWED", "Widowed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="patient_profile")
    mrn = models.CharField(max_length=32, unique=True, db_index=True, editable=False)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=16, choices=[
        ("MALE", "Male"), ("FEMALE", "Female"), ("OTHER", "Other"), ("UNKNOWN", "Unknown")
    ], default="UNKNOWN")
    blood_group = models.CharField(max_length=8, choices=BloodGroup.choices, default=BloodGroup.UNKNOWN)
    marital_status = models.CharField(max_length=16, choices=MaritalStatus.choices, default=MaritalStatus.SINGLE)
    primary_language = models.CharField(max_length=64, default="English")
    is_organ_donor = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hs_patient_profiles"
        ordering = ["user__last_name", "user__first_name"]

    def save(self, *args, **kwargs):
        if not self.mrn:
            self.mrn = generate_medical_record_number("MRN")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.mrn})"

class EmergencyContact(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="emergency_contacts")
    name = models.CharField(max_length=150)
    relationship = models.CharField(max_length=64, choices=[
        ("SPOUSE", "Spouse"), ("PARENT", "Parent"), ("CHILD", "Child"),
        ("SIBLING", "Sibling"), ("GUARDIAN", "Legal Guardian"), ("FRIEND", "Friend")
    ])
    phone_number = models.CharField(max_length=32)
    email = models.EmailField(blank=True)
    is_primary = models.BooleanField(default=True)

    class Meta:
        db_table = "hs_patient_emergency_contacts"

    def __str__(self):
        return f"{self.name} ({self.relationship}) - {self.phone_number}"

class Allergy(models.Model):
    class AllergenCategory(models.TextChoices):
        MEDICATION = "MEDICATION", "Medication / Pharmacology"
        FOOD = "FOOD", "Food Allergen"
        ENVIRONMENTAL = "ENVIRONMENTAL", "Environmental / Seasonal"
        BIOLOGICAL = "BIOLOGICAL", "Latex / Biological Product"

    class Severity(models.TextChoices):
        MILD = "MILD", "Mild (Rash, Itching)"
        MODERATE = "MODERATE", "Moderate (Hives, Facial Swelling)"
        SEVERE = "SEVERE", "Severe Anaphylaxis (Airway Compromise)"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="allergies")
    allergen_name = models.CharField(max_length=150, db_index=True)
    category = models.CharField(max_length=32, choices=AllergenCategory.choices, default=AllergenCategory.MEDICATION)
    severity = models.CharField(max_length=32, choices=Severity.choices, default=Severity.MODERATE)
    reaction_description = models.TextField()
    diagnosed_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "hs_patient_allergies"

    def __str__(self):
        return f"{self.allergen_name} ({self.severity}) - {self.patient}"

class MedicalHistory(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="medical_history")
    condition_name = models.CharField(max_length=255)
    icd10_code = models.CharField(max_length=32, blank=True)
    diagnosed_year = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[
        ("ACTIVE", "Active Chronic Condition"),
        ("IN_REMISSION", "In Remission"),
        ("RESOLVED", "Resolved Historical Event")
    ], default="ACTIVE")
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "hs_patient_medical_history"


class SurgicalHistory(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="surgical_history")
    procedure_name = models.CharField(max_length=255)
    surgery_year = models.PositiveIntegerField()
    hospital_name = models.CharField(max_length=255, blank=True)
    complications = models.TextField(blank=True)

    class Meta:
        db_table = "hs_patient_surgical_history"


class FamilyHistory(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="family_history")
    relative_relationship = models.CharField(max_length=64)
    condition_name = models.CharField(max_length=255)
    age_at_onset = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        db_table = "hs_patient_family_history"

class VitalSign(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="vital_signs")
    systolic_bp = models.PositiveIntegerField(help_text="mmHg")
    diastolic_bp = models.PositiveIntegerField(help_text="mmHg")
    heart_rate = models.PositiveIntegerField(help_text="beats per minute")
    respiratory_rate = models.PositiveIntegerField(help_text="breaths per minute", default=16)
    temperature_celsius = models.DecimalField(max_digits=4, decimal_places=1, default=37.0)
    spo2_percentage = models.PositiveIntegerField(help_text="SpO2 percentage (0-100)", default=98)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    height_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    bmi = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    recorded_at = models.DateTimeField(default=timezone.now, db_index=True)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "hs_patient_vitals"
        ordering = ["-recorded_at"]

    def calculate_bmi(self):
        if self.weight_kg and self.height_cm and self.height_cm > 0:
            h_m = float(self.height_cm) / 100.0
            return round(float(self.weight_kg) / (h_m * h_m), 1)
        return None

    def calculate_mean_arterial_pressure(self):
        return round((2 * self.diastolic_bp + self.systolic_bp) / 3.0, 1)

    def save(self, *args, **kwargs):
        if not self.bmi:
            self.bmi = self.calculate_bmi()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"BP {self.systolic_bp}/{self.diastolic_bp} HR {self.heart_rate} SpO2 {self.spo2_percentage}% ({self.recorded_at.strftime('%Y-%m-%d %H:%M')})"
