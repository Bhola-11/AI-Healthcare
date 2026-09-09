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

from .models import DrugInteractionRule

class DrugSafetyEngineService:
    @staticmethod
    def check_interaction(drug_a_name, drug_b_name):
        rule = DrugInteractionRule.objects.filter(
            models.Q(drug_a__iexact=drug_a_name, drug_b__iexact=drug_b_name) |
            models.Q(drug_a__iexact=drug_b_name, drug_b__iexact=drug_a_name)
        ).first()
        return rule

    @staticmethod
    def screen_prescription_safety(patient, proposed_medication_name):
        warnings = []
        # Check patient allergies
        for allergy in patient.allergies.filter(is_active=True):
            if allergy.allergen_name.lower() in proposed_medication_name.lower():
                warnings.append({
                    "type": "ALLERGY_CONTRAINDICATION",
                    "severity": "CRITICAL",
                    "details": f"Patient has documented allergy to {allergy.allergen_name} ({allergy.get_severity_display()})."
                })
        return warnings

from apps.clinical_records.models import ICD10DiagnosisCode

class DiagnosticSuggestionService:
    KEYWORD_MAP = {
        "hypertension": ["I10"],
        "high blood pressure": ["I10"],
        "diabetes": ["E11.9"],
        "hyperglycemia": ["E11.65"],
        "asthma": ["J45.909"],
        "wheezing": ["J45.909"],
        "copd": ["J44.9"],
        "pneumonia": ["J18.9"],
        "fever": ["R50.9"],
        "cough": ["R05"],
        "back pain": ["M54.5"],
        "chest pain": ["I25.10"],
        "heart failure": ["I50.9"],
        "gerd": ["K21.9"],
        "acid reflux": ["K21.9"],
        "anxiety": ["F41.1"],
        "depression": ["F32.9"],
    }

    @classmethod
    def suggest_diagnoses(cls, clinical_text):
        if not clinical_text:
            return []
        text_lower = clinical_text.lower()
        matched_codes = set()
        for kw, codes in cls.KEYWORD_MAP.items():
            if kw in text_lower:
                matched_codes.update(codes)
                
        return list(ICD10DiagnosisCode.objects.filter(code__in=matched_codes))
