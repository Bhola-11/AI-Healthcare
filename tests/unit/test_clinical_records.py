from datetime import datetime
from django.test import TestCase
from apps.accounts.models import User
from apps.facilities.models import Facility
from apps.doctors.models import DoctorProfile
from apps.patients.models import PatientProfile
from apps.clinical_records.models import Encounter, SOAPNote, ICD10DiagnosisCode, EncounterDiagnosis

class ClinicalRecordsTestCase(TestCase):
    def setUp(self):
        self.doc_user = User.objects.create_user(email="dr.emr@test.org", password="Pass123!", role=User.Role.DOCTOR)
        self.pat_user = User.objects.create_user(email="pat.emr@test.org", password="Pass123!", role=User.Role.PATIENT)
        self.facility = Facility.objects.create(name="EMR Clinic", facility_code="EMR-01", license_number="L-EMR", phone="123", email="e@e.org", address_line_1="A1", city="C", state="S", postal_code="000")
        self.doctor = DoctorProfile.objects.create(user=self.doc_user, npi_number="1122334455", license_number="L-EMR-DOC", license_expiry_date=datetime(2028, 1, 1).date())
        self.patient = PatientProfile.objects.create(user=self.pat_user)
        self.icd10 = ICD10DiagnosisCode.objects.create(code="E11.9", description="Type 2 diabetes mellitus without complications", chapter_number=4, chapter_title="Endocrine")

    def test_encounter_and_soap_note_workflow(self):
        enc = Encounter.objects.create(
            encounter_number="ENC-001",
            patient=self.patient,
            doctor=self.doctor,
            facility=self.facility
        )
        soap = SOAPNote.objects.create(
            encounter=enc,
            subjective="Patient reports increased polydipsia and polyuria.",
            objective="Random Blood Glucose: 210 mg/dL. Vitals stable.",
            assessment="Uncontrolled Type 2 Diabetes Mellitus.",
            plan="Initiate Metformin 500mg BID. Nutritional counseling."
        )
        self.assertFalse(soap.is_signed)
        soap.sign_note()
        self.assertTrue(soap.is_signed)
        self.assertIsNotNone(soap.signed_at)

        # Link diagnosis
        diag = EncounterDiagnosis.objects.create(
            encounter=enc,
            icd10=self.icd10,
            diagnosis_type=EncounterDiagnosis.DiagnosisType.PRIMARY
        )
        self.assertEqual(diag.icd10.code, "E11.9")
