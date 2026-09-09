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
