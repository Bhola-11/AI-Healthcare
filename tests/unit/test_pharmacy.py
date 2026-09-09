from datetime import date, timedelta
from django.test import TestCase
from django.utils import timezone
from apps.accounts.models import User
from apps.patients.models import PatientProfile
from apps.doctors.models import DoctorProfile
from apps.prescriptions.models import Prescription, PrescriptionItem
from apps.pharmacy.models import Medication, BatchInventory, DispensationRecord

class PharmacyTestCase(TestCase):
    def setUp(self):
        self.doc_user = User.objects.create_user(email="dr.rx@test.org", password="Pass123!", role=User.Role.DOCTOR)
        self.pat_user = User.objects.create_user(email="pat.rx@test.org", password="Pass123!", role=User.Role.PATIENT)
        self.doctor = DoctorProfile.objects.create(user=self.doc_user, npi_number="7788990011", license_number="L-RX", license_expiry_date=date(2028, 1, 1))
        self.patient = PatientProfile.objects.create(user=self.pat_user)
        self.med = Medication.objects.create(
            brand_name="Glucophage",
            generic_name="Metformin Hydrochloride",
            atc_code="A10BA02",
            drug_class="Biguanide",
            strength="500 mg"
        )
        self.batch = BatchInventory.objects.create(
            medication=self.med,
            batch_number="MET-2026-A",
            manufacturing_date=date(2025, 1, 1),
            expiry_date=date(2027, 1, 1),
            quantity_received=500,
            quantity_on_hand=500
        )

    def test_prescription_and_dispensation(self):
        rx = Prescription.objects.create(
            rx_number="RX-TEST-001",
            patient=self.patient,
            doctor=self.doctor,
            expires_at=date(2026, 12, 31)
        )
        item = PrescriptionItem.objects.create(
            prescription=rx,
            medication_name="Metformin Hydrochloride",
            dosage="500 mg",
            quantity=60
        )
        self.assertTrue(len(rx.signature_hash) == 64)

        # Dispense
        self.batch.quantity_on_hand -= item.quantity
        self.batch.save()
        DispensationRecord.objects.create(batch=self.batch, rx_item_id=item.id, quantity_dispensed=60)
        self.assertEqual(self.batch.quantity_on_hand, 440)
