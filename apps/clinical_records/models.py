import uuid
from django.db import models
from django.utils import timezone
from apps.patients.models import PatientProfile
from apps.doctors.models import DoctorProfile
from apps.facilities.models import Facility
from apps.appointments.models import Appointment


class Encounter(models.Model):
    class EncounterClass(models.TextChoices):
        AMBULATORY = "AMBULATORY", "Outpatient Ambulatory Visit"
        EMERGENCY = "EMERGENCY", "Emergency Department Visit"
        INPATIENT = "INPATIENT", "Inpatient Hospital Admission"
        TELEMEDICINE = "TELEMEDICINE", "Virtual Telemedicine Encounter"
        HOME_HEALTH = "HOME_HEALTH", "Home Health Care Visit"

    class EncounterStatus(models.TextChoices):
        PLANNED = "PLANNED", "Planned / Scheduled"
        ARRIVED = "ARRIVED", "Patient Arrived"
        IN_PROGRESS = "IN_PROGRESS", "Clinical Consultation Active"
        ON_HOLD = "ON_HOLD", "On Hold (Pending Diagnostics)"
        FINISHED = "FINISHED", "Encounter Signed & Closed"
        CANCELLED = "CANCELLED", "Encounter Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    encounter_number = models.CharField(max_length=32, unique=True, db_index=True)
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="encounters")
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name="encounters")
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name="encounters")
    appointment = models.OneToOneField(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name="encounter")
    
    encounter_class = models.CharField(max_length=32, choices=EncounterClass.choices, default=EncounterClass.AMBULATORY)
    status = models.CharField(max_length=32, choices=EncounterStatus.choices, default=EncounterStatus.IN_PROGRESS, db_index=True)
    
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    discharge_disposition = models.CharField(max_length=64, blank=True, choices=[
        ("ROUTINE", "Discharged to Home / Routine"),
        ("ADMIT", "Admitted to Inpatient Ward"),
        ("TRANSFER", "Transferred to Tertiary Center"),
        ("AMA", "Left Against Medical Advice"),
        ("EXPIRED", "Patient Expired")
    ])
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hs_clinical_encounters"
        ordering = ["-start_time"]

    def __str__(self):
        return f"Encounter #{self.encounter_number} - {self.patient} with Dr. {self.doctor.user.get_full_name()}"

class SOAPNote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    encounter = models.OneToOneField(Encounter, on_delete=models.CASCADE, related_name="soap_note")
    
    # Subjective: Patient symptoms, history of present illness (HPI), review of systems (ROS)
    subjective = models.TextField(help_text="Chief complaint, HPI, review of systems, patient-reported symptoms.")
    
    # Objective: Physical examination findings, vital signs observed, lab data
    objective = models.TextField(help_text="Physical exam findings, clinical observations, physical inspection.")
    
    # Assessment: Medical appraisal, differential diagnoses, clinical reasoning
    assessment = models.TextField(help_text="Clinical synthesis, diagnostic impressions, disease staging.")
    
    # Plan: Therapeutic orders, medications, procedures, patient education, follow-up
    plan = models.TextField(help_text="Management plan, e-prescriptions, diagnostic orders, lifestyle advisories.")
    
    is_signed = models.BooleanField(default=False)
    signed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hs_clinical_soap_notes"

    def sign_note(self):
        self.is_signed = True
        self.signed_at = timezone.now()
        self.save()

class ICD10DiagnosisCode(models.Model):
    code = models.CharField(max_length=16, primary_key=True, db_index=True)
    description = models.CharField(max_length=512, db_index=True)
    chapter_number = models.PositiveIntegerField(default=1)
    chapter_title = models.CharField(max_length=255)
    category_code = models.CharField(max_length=16, db_index=True)
    is_billable = models.BooleanField(default=True)
    is_chronic = models.BooleanField(default=False)

    class Meta:
        db_table = "hs_icd10_diagnosis_codes"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.description}"

class EncounterDiagnosis(models.Model):
    class DiagnosisType(models.TextChoices):
        PRIMARY = "PRIMARY", "Primary / Principal Diagnosis"
        SECONDARY = "SECONDARY", "Secondary Comorbidity"
        DIFFERENTIAL = "DIFFERENTIAL", "Differential Working Diagnosis"
        DISCHARGE = "DISCHARGE", "Final Discharge Diagnosis"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    encounter = models.ForeignKey(Encounter, on_delete=models.CASCADE, related_name="diagnoses")
    icd10 = models.ForeignKey(ICD10DiagnosisCode, on_delete=models.CASCADE, related_name="encounter_diagnoses")
    diagnosis_type = models.CharField(max_length=32, choices=DiagnosisType.choices, default=DiagnosisType.PRIMARY)
    clinical_notes = models.TextField(blank=True)
    recorded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "hs_encounter_diagnoses"

    def __str__(self):
        return f"{self.icd10.code} ({self.diagnosis_type}) - {self.encounter}"

class ClinicalAttachment(models.Model):
    class AttachmentType(models.TextChoices):
        XRAY = "XRAY", "X-Ray Radiograph"
        MRI = "MRI", "Magnetic Resonance Imaging (MRI)"
        CT_SCAN = "CT_SCAN", "Computed Tomography (CT)"
        ULTRASOUND = "ULTRASOUND", "Ultrasound Sonogram"
        ECG = "ECG", "Electrocardiogram (ECG/EKG)"
        LAB_SCAN = "LAB_SCAN", "Scanned Laboratory Report"
        PATHOLOGY = "PATHOLOGY", "Histopathology Slide Image"
        DISCHARGE_DOC = "DISCHARGE_DOC", "Discharge Summary Document"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    encounter = models.ForeignKey(Encounter, on_delete=models.CASCADE, related_name="attachments")
    attachment_type = models.CharField(max_length=32, choices=AttachmentType.choices)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="clinical_attachments/%Y/%m/")
    mime_type = models.CharField(max_length=64, default="application/pdf")
    file_size_bytes = models.PositiveBigIntegerField(default=0)
    uploaded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "hs_clinical_attachments"

    def __str__(self):
        return f"{self.title} ({self.attachment_type}) - {self.encounter}"
