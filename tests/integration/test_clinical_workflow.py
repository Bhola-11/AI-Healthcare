from decimal import Decimal
from django.test import TestCase, Client
from django.utils import timezone
from apps.accounts.models import User
from apps.facilities.models import Facility, Department, Ward, Room, Bed
from apps.doctors.models import DoctorProfile, Specialty
from apps.patients.models import PatientProfile, VitalSign, Allergy
from apps.appointments.models import Appointment
from apps.clinical_records.models import Encounter, SOAPNote, ICD10DiagnosisCode, EncounterDiagnosis
from apps.prescriptions.models import Prescription, PrescriptionItem
from apps.pharmacy.models import Medication, BatchInventory, DispensationRecord
from apps.laboratory.models import LabTestCatalog, LabOrder, LabSpecimen, LabResultItem
from apps.billing.models import Invoice, InvoiceItem, Payment
from apps.insurance.models import InsuranceProvider, PatientInsurancePolicy, InsuranceClaim
from apps.insurance.services import ClaimAdjudicationService

class EndToEndClinicalWorkflowIntegrationTestCase(TestCase):
    def setUp(self):
        # 1. Foundation Users
        self.doc_user = User.objects.create_user(email="chief.physician@hospital.org", password="DoctorPass123!", role=User.Role.DOCTOR, first_name="Gregory", last_name="House")
        self.pat_user = User.objects.create_user(email="patient.lifecycle@hospital.org", password="PatientPass123!", role=User.Role.PATIENT, first_name="John", last_name="Doe")
        self.nurse_user = User.objects.create_user(email="triage.nurse@hospital.org", password="NursePass123!", role=User.Role.NURSE, first_name="Florence", last_name="Nightingale")
        self.biller_user = User.objects.create_user(email="biller@hospital.org", password="BillerPass123!", role=User.Role.BILLING, first_name="Bob", last_name="Cash")

        # 2. Facility & Specialty
        self.facility = Facility.objects.create(name="St. Jude Memorial Hospital", facility_type=Facility.FacilityType.GENERAL_HOSPITAL, license_number="HOSP-9901")
        self.dept = Department.objects.create(facility=self.facility, name="Cardiology")
        self.spec = Specialty.objects.create(name="Cardiovascular Medicine", code="CARD-01")
        self.doctor = DoctorProfile.objects.create(user=self.doc_user, specialty=self.spec, license_number="MD-NY-8821")
        self.patient = PatientProfile.objects.create(user=self.pat_user)

    def test_complete_hospital_patient_journey(self):
        # Step 1: Patient Admission / Triage & Vitals
        vitals = VitalSign.objects.create(
            patient=self.patient,
            systolic_bp=145,
            diastolic_bp=92,
            heart_rate=88,
            respiratory_rate=18,
            temperature_celsius=Decimal("37.2"),
            spo2_percentage=98,
            height_cm=Decimal("178.0"),
            weight_kg=Decimal("82.5"),
            recorded_by=self.nurse_user
        )
        self.assertAlmostEqual(float(vitals.bmi), 26.04, places=1)
        self.assertAlmostEqual(float(vitals.mean_arterial_pressure), 109.67, places=1)

        # Step 2: Book Doctor Appointment
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            facility=self.facility,
            scheduled_start=timezone.now() + timezone.timedelta(hours=1),
            scheduled_end=timezone.now() + timezone.timedelta(hours=2),
            reason_for_visit="Severe recurring hypertension & exertional chest discomfort",
            status=Appointment.Status.CHECKED_IN
        )
        self.assertEqual(appointment.status, Appointment.Status.CHECKED_IN)

        # Step 3: Clinical Encounter & Structured SOAP Note
        encounter = Encounter.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            facility=self.facility,
            encounter_type=Encounter.EncounterType.OUTPATIENT,
            status=Encounter.Status.IN_PROGRESS
        )
        dx_code = ICD10DiagnosisCode.objects.create(code="I10", description="Essential (primary) hypertension")
        EncounterDiagnosis.objects.create(encounter=encounter, diagnosis_code=dx_code, is_primary=True)

        soap = SOAPNote.objects.create(
            encounter=encounter,
            subjective="Patient reports intermittent retrosternal chest tightness lasting 10 minutes on exertion.",
            objective="BP 145/92 mmHg, S1/S2 distinct, no peripheral edema. Lungs clear.",
            assessment="Stage 2 Primary Essential Hypertension, rule out CAD.",
            plan="Initiate Amlodipine 5mg daily. Order Serum Electrolytes & Troponin-I. Lifestyle modification.",
            author=self.doc_user
        )
        soap.sign(self.doc_user)
        self.assertTrue(soap.is_signed)
        self.assertIsNotNone(soap.digital_signature_hash)

        # Step 4: Diagnostic Laboratory Orders & Pathology Sign-off
        lab_test = LabTestCatalog.objects.create(code="TROP-I", name="Troponin-I High Sensitivity", department="Biochemistry", cost_amount=Decimal("45.00"))
        lab_order = LabOrder.objects.create(patient=self.patient, encounter=encounter, ordering_physician=self.doc_user, priority=LabOrder.Priority.STAT)
        specimen = LabSpecimen.objects.create(order=lab_order, specimen_type="Serum Blood", barcode="BARC-TROPI-990")
        
        result_item = LabResultItem.objects.create(
            order=lab_order,
            test_catalog=lab_test,
            test_name=lab_test.name,
            observed_numeric_value=Decimal("0.02"),
            unit="ng/mL",
            flag=LabResultItem.Flag.NORMAL
        )
        self.assertEqual(result_item.flag, LabResultItem.Flag.NORMAL)

        # Step 5: Electronic Prescription & Pharmacy Dispensation
        prescription = Prescription.objects.create(patient=self.patient, doctor=self.doctor, encounter=encounter)
        med = Medication.objects.create(brand_name="Norvasc", generic_name="Amlodipine Besylate", strength="5mg", dosage_form="Tablet", atc_code="C08CA01")
        batch = BatchInventory.objects.create(medication=med, batch_number="BAT-NORV-001", quantity_on_hand=500, cost_per_unit=Decimal("0.25"), unit_selling_price=Decimal("1.20"), expiry_date=timezone.now().date() + timezone.timedelta(days=365))
        
        item = PrescriptionItem.objects.create(prescription=prescription, medication_name=med.brand_name, dosage="5mg", route="Oral", frequency="Once daily in morning", duration_days=30, quantity=30)
        prescription.sign_prescription()
        self.assertTrue(prescription.is_signed)

        # Dispense at Pharmacy
        dispense = DispensationRecord.objects.create(
            prescription_item=item,
            batch=batch,
            quantity_dispensed=30,
            pharmacist_notes="Verified dosage, patient educated on hypotension symptoms."
        )
        batch.refresh_from_db()
        self.assertEqual(batch.quantity_on_hand, 470)

        # Step 6: Billing & Invoicing
        invoice = Invoice.objects.create(patient=self.patient, encounter=encounter, due_date=timezone.now().date() + timezone.timedelta(days=30))
        InvoiceItem.objects.create(invoice=invoice, item_type=InvoiceItem.ItemType.CONSULTATION, description="Specialist Consultation", quantity=1, unit_price=Decimal("150.00"), total_amount=Decimal("150.00"))
        InvoiceItem.objects.create(invoice=invoice, item_type=InvoiceItem.ItemType.LABORATORY, description="Troponin-I High Sensitivity", quantity=1, unit_price=Decimal("45.00"), total_amount=Decimal("45.00"))
        InvoiceItem.objects.create(invoice=invoice, item_type=InvoiceItem.ItemType.PHARMACY, description="Amlodipine Besylate 5mg (30 Tabs)", quantity=30, unit_price=Decimal("1.20"), total_amount=Decimal("36.00"))
        invoice.recalculate_totals()
        self.assertEqual(invoice.total_amount, Decimal("231.00"))

        # Step 7: Insurance Adjudication & Payment Settlement
        payor = InsuranceProvider.objects.create(name="Aetna Global Health", payer_id="AETNA-001")
        policy = PatientInsurancePolicy.objects.create(patient=self.patient, provider=payor, policy_number="POL-AET-994", group_number="GRP-881", copay_amount=Decimal("30.00"), coinsurance_rate=Decimal("20.00"))
        claim = InsuranceClaim.objects.create(patient=self.patient, policy=policy, encounter=encounter, total_claimed_amount=Decimal("231.00"))
        
        adjudicated = ClaimAdjudicationService.adjudicate(claim)
        self.assertEqual(adjudicated.approved_amount, Decimal("184.80"))

        # Step 8: Patient Co-Pay Settlement
        Payment.objects.create(invoice=invoice, amount=Decimal("46.20"), payment_method=Payment.PaymentMethod.CREDIT_CARD, transaction_reference="TXN-PAY-0091")
        invoice.refresh_from_db()
        self.assertEqual(invoice.amount_paid, Decimal("46.20"))
        self.assertEqual(invoice.balance_due, Decimal("184.80"))
