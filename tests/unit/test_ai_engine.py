from django.test import TestCase
from apps.accounts.models import User
from apps.patients.models import PatientProfile, Allergy, VitalSign
from apps.ai_engine.models import ClinicalTriageAssessment, DrugInteractionRule
from apps.ai_engine.services import TriageEngineService, DrugSafetyEngineService, DiagnosticSuggestionService

class AIEngineTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="pat.ai@test.org", password="Pass123!", role=User.Role.PATIENT)
        self.patient = PatientProfile.objects.create(user=self.user)
        Allergy.objects.create(patient=self.patient, allergen_name="Penicillin", reaction_description="Severe hives")
        DrugInteractionRule.objects.create(
            drug_a="Warfarin",
            drug_b="Aspirin",
            severity=DrugInteractionRule.Severity.MAJOR,
            clinical_mechanism="Additive platelet inhibition and vitamin K antagonism.",
            management_advice="Avoid combination or monitor INR closely."
        )

    def test_triage_resuscitation(self):
        assessment = TriageEngineService.evaluate(
            patient=self.patient,
            complaint="Unresponsive, cyanotic",
            flags=["cardiac_arrest"]
        )
        self.assertEqual(assessment.urgency_level, ClinicalTriageAssessment.UrgencyLevel.LEVEL_1_RESUSCITATION)

    def test_allergy_screening(self):
        warnings = DrugSafetyEngineService.screen_prescription_safety(self.patient, "Amoxicillin Clavulanate")
        self.assertEqual(len(warnings), 0) # Penicillin != Amoxicillin string check
        warnings_pen = DrugSafetyEngineService.screen_prescription_safety(self.patient, "Penicillin V Potassium")
        self.assertEqual(len(warnings_pen), 1)

    def test_diagnostic_suggestion(self):
        suggestions = DiagnosticSuggestionService.suggest_diagnoses("Patient has history of hypertension and wheezing asthma.")
        self.assertTrue(len(suggestions) >= 1)
