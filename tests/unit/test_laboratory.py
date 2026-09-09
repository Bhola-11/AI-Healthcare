from datetime import date
from django.test import TestCase
from decimal import Decimal
from apps.accounts.models import User
from apps.patients.models import PatientProfile
from apps.doctors.models import DoctorProfile
from apps.laboratory.models import SpecimenType, LabTestCatalog, DemographicReferenceRange, LabOrder, LabResultItem
from apps.laboratory.services import CriticalLabAlertService

class LaboratoryTestCase(TestCase):
    def setUp(self):
        self.doc_user = User.objects.create_user(email="dr.lab@test.org", password="Pass123!", role=User.Role.DOCTOR)
        self.pat_user = User.objects.create_user(email="pat.lab@test.org", password="Pass123!", role=User.Role.PATIENT)
        self.doctor = DoctorProfile.objects.create(user=self.doc_user, npi_number="3344556677", license_number="L-LAB", license_expiry_date=date(2028, 1, 1))
        self.patient = PatientProfile.objects.create(user=self.pat_user)
        self.specimen = SpecimenType.objects.create(name="Whole Blood", code="BLD-WB", container_type="Lavender EDTA")
        self.test = LabTestCatalog.objects.create(
            loinc_code="718-7",
            test_name="Hemoglobin",
            specimen_type=self.specimen,
            measurement_unit="g/dL"
        )
        self.range = DemographicReferenceRange.objects.create(
            test=self.test,
            normal_min=Decimal("12.0"),
            normal_max=Decimal("16.0"),
            critical_low=Decimal("7.0"),
            critical_high=Decimal("20.0")
        )

    def test_flag_calculation_and_critical_alert(self):
        order = LabOrder.objects.create(
            order_number="LAB-TEST-001",
            patient=self.patient,
            ordering_doctor=self.doctor
        )
        res = LabResultItem.objects.create(
            order=order,
            test=self.test,
            observed_numeric_value=Decimal("6.5")
        )
        self.assertEqual(res.flag, LabResultItem.Flag.CRITICAL_LOW)
        
        # Test critical alert dispatch
        alert_sent = CriticalLabAlertService.notify_critical_result(res)
        self.assertTrue(alert_sent)
