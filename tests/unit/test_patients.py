from datetime import date
from django.test import TestCase
from apps.accounts.models import User
from apps.patients.models import PatientProfile, VitalSign, Allergy
from apps.patients.services import VitalsAnalyticsService

class PatientTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="patient.clara@example.com",
            password="PatientPassword123!",
            first_name="Clara",
            last_name="Oswald",
            role=User.Role.PATIENT
        )
        self.patient = PatientProfile.objects.create(
            user=self.user,
            date_of_birth=date(1990, 5, 12),
            gender="FEMALE",
            blood_group=PatientProfile.BloodGroup.O_POS
        )

    def test_mrn_generation(self):
        self.assertTrue(self.patient.mrn.startswith("MRN-"))
        self.assertEqual(len(self.patient.mrn), 12)

    def test_vitals_calculations(self):
        v = VitalSign.objects.create(
            patient=self.patient,
            systolic_bp=120,
            diastolic_bp=80,
            heart_rate=72,
            weight_kg=65.0,
            height_cm=165.0
        )
        self.assertEqual(v.calculate_mean_arterial_pressure(), 93.3)
        self.assertEqual(v.bmi, 23.9)

    def test_analytics_service(self):
        VitalSign.objects.create(patient=self.patient, systolic_bp=122, diastolic_bp=82, heart_rate=75)
        trends = VitalsAnalyticsService.get_vitals_trend_series(self.patient.id)
        self.assertEqual(len(trends["systolic"]), 1)
