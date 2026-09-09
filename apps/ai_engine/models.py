import uuid
from django.db import models
from django.utils import timezone
from apps.patients.models import PatientProfile
from apps.doctors.models import DoctorProfile
from apps.clinical_records.models import Encounter


class ClinicalTriageAssessment(models.Model):
    class UrgencyLevel(models.IntegerChoices):
        LEVEL_1_RESUSCITATION = 1, "Level 1: Immediate Resuscitation (Red)"
        LEVEL_2_EMERGENT = 2, "Level 2: Very Urgent / Emergent (Orange)"
        LEVEL_3_URGENT = 3, "Level 3: Urgent (Yellow)"
        LEVEL_4_LESS_URGENT = 4, "Level 4: Standard / Less Urgent (Green)"
        LEVEL_5_NON_URGENT = 5, "Level 5: Non-Urgent (Blue)"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="triage_assessments")
    encounter = models.ForeignKey(Encounter, on_delete=models.SET_NULL, null=True, blank=True, related_name="triage_assessments")
    presenting_complaint = models.CharField(max_length=255)
    urgency_level = models.IntegerField(choices=UrgencyLevel.choices, default=UrgencyLevel.LEVEL_3_URGENT, db_index=True)
    discriminator_flags = models.JSONField(default=list, help_text="Clinical red flags observed")
    pain_score = models.PositiveIntegerField(default=0, help_text="Pain scale 0-10")
    recommended_disposition = models.CharField(max_length=255)
    assessed_by = models.CharField(max_length=255, default="Triage Assessment Engine")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "hs_ai_triage_assessments"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Triage #{self.id} for {self.patient} - {self.get_urgency_level_display()}"

class DrugInteractionRule(models.Model):
    class Severity(models.TextChoices):
        CONTRAINDICATED = "CONTRAINDICATED", "Strictly Contraindicated (Severe Harm / Fatal)"
        MAJOR = "MAJOR", "Major Interaction (Requires Doctor Override)"
        MODERATE = "MODERATE", "Moderate (Clinical Monitoring Recommended)"
        MINOR = "MINOR", "Minor Interaction"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    drug_a = models.CharField(max_length=150, db_index=True)
    drug_b = models.CharField(max_length=150, db_index=True)
    severity = models.CharField(max_length=32, choices=Severity.choices, default=Severity.MAJOR)
    clinical_mechanism = models.TextField()
    management_advice = models.TextField()
    evidence_source = models.CharField(max_length=255, default="FDA Drug Safety Database / Micromedex")

    class Meta:
        db_table = "hs_ai_drug_interaction_rules"
        unique_together = ("drug_a", "drug_b")

    def __str__(self):
        return f"{self.drug_a} + {self.drug_b} ({self.severity})"

class ClinicalRiskScoreLog(models.Model):
    class RiskCategory(models.TextChoices):
        LOW = "LOW", "Low Clinical Risk"
        MODERATE = "MODERATE", "Moderate Risk"
        HIGH = "HIGH", "High Clinical Risk"
        VERY_HIGH = "VERY_HIGH", "Critical / Very High Risk"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="risk_scores")
    score_name = models.CharField(max_length=64, help_text="e.g. Framingham 10-Year ASCVD, Glasgow-Blatchford")
    calculated_score = models.DecimalField(max_digits=6, decimal_places=2)
    risk_category = models.CharField(max_length=32, choices=RiskCategory.choices, default=RiskCategory.LOW)
    explanation = models.TextField()
    calculated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "hs_ai_risk_score_logs"
        ordering = ["-calculated_at"]

class AIInferenceAuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model_name = models.CharField(max_length=64)
    input_payload = models.JSONField(default=dict)
    output_payload = models.JSONField(default=dict)
    is_overridden = models.BooleanField(default=False)
    doctor_override_reason = models.TextField(blank=True)
    latency_ms = models.PositiveIntegerField(default=12)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "hs_ai_inference_audit_logs"
