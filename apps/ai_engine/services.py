from .models import ClinicalTriageAssessment

class TriageEngineService:
    RED_FLAGS = {
        "cardiac_arrest": (1, "Immediate resuscitation required: unresponsive or severe shock."),
        "airway_compromise": (1, "Immediate intubation or airway intervention needed."),
        "chest_pain_diaphoretic": (2, "Suspected acute coronary syndrome (ACS). Rapid ECG required."),
        "acute_stroke_signs": (2, "Possible acute ischemic stroke (FAST positive). Urgent CT brain."),
        "severe_respiratory_distress": (2, "SpO2 < 90% on room air, stridor, or accessory muscle use."),
        "moderate_pain": (3, "Pain score 4-7, stable vital signs."),
        "minor_laceration": (4, "Controlled bleeding, intact neurovascular examination."),
        "chronic_refill": (5, "Non-urgent prescription renewal without acute distress."),
    }

    @classmethod
    def evaluate(cls, patient, complaint, vitals=None, pain_score=0, flags=None):
        flags = flags or []
        urgency = ClinicalTriageAssessment.UrgencyLevel.LEVEL_4_LESS_URGENT
        disposition = "Standard outpatient clinic queue"

        # Check vitals red flags
        if vitals:
            if vitals.spo2_percentage and vitals.spo2_percentage < 90:
                flags.append("severe_respiratory_distress")
            if vitals.systolic_bp and vitals.systolic_bp < 80:
                flags.append("cardiac_arrest")

        # Evaluate highest priority flag
        if any(f in flags for f in ["cardiac_arrest", "airway_compromise"]):
            urgency = ClinicalTriageAssessment.UrgencyLevel.LEVEL_1_RESUSCITATION
            disposition = "IMMEDIATE RESUSCITATION BAY (Level 1)"
        elif any(f in flags for f in ["chest_pain_diaphoretic", "acute_stroke_signs", "severe_respiratory_distress"]):
            urgency = ClinicalTriageAssessment.UrgencyLevel.LEVEL_2_EMERGENT
            disposition = "Emergency Department Bed - Immediate Physician Evaluation (<10 min)"
        elif pain_score >= 7 or "moderate_pain" in flags:
            urgency = ClinicalTriageAssessment.UrgencyLevel.LEVEL_3_URGENT
            disposition = "Urgent Treatment Area - Evaluation within 30 minutes"
        elif "minor_laceration" in flags:
            urgency = ClinicalTriageAssessment.UrgencyLevel.LEVEL_4_LESS_URGENT
            disposition = "Fast Track Ambulatory Care"
        elif "chronic_refill" in flags:
            urgency = ClinicalTriageAssessment.UrgencyLevel.LEVEL_5_NON_URGENT
            disposition = "Routine Outpatient Appointment"

        return ClinicalTriageAssessment.objects.create(
            patient=patient,
            presenting_complaint=complaint,
            urgency_level=urgency,
            discriminator_flags=flags,
            pain_score=pain_score,
            recommended_disposition=disposition
        )
