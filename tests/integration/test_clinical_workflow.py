import uuid
from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from apps.accounts.models import User
from apps.facilities.models import Facility, Department
from apps.doctors.models import DoctorProfile, Specialty, DoctorSpecialty
from apps.patients.models import PatientProfile, VitalSign
from apps.appointments.models import Appointment
from apps.clinical_records.models import Encounter, SOAPNote, ICD10DiagnosisCode, EncounterDiagnosis
from apps.prescriptions.models import Prescription, PrescriptionItem
from apps.pharmacy.models import Medication, BatchInventory, DispensationRecord
from apps.laboratory.models import SpecimenType, LabTestCatalog, DemographicReferenceRange, LabOrder, LabResultItem
from apps.billing.models import FeeSchedule, Invoice, InvoiceItem, Payment
from apps.insurance.models import InsuranceProvider, PatientInsurancePolicy, InsuranceClaim
from apps.insurance.services import ClaimAdjudicationService

class EndToEndClinicalWorkflowIntegrationTestCase(TestCase):
    def setUp(self):
        # 1. Foundation Users
        self.doc_user = User.objects.create_user(email="chief.physician@hospital.org", password="DoctorPass123!", role=User.Role.DOCTOR, first_name="Gregory", last_name="House")
        self.pat_user = User.objects.create_user(email="patient.lifecycle@hospital.org", password="PatientPass123!", role=User.Role.PATIENT, first_name="John", last_name="Doe")
        self.nurse_user = User.objects.create_user(email="triage.nurse@hospital.org", password="NursePass123!", role=User.Role.NURSE, first_name="Florence", last_name="Nightingale")
        self.biller_user = User.objects.create_user(email="biller@hospital.org", password="BillerPass123!", role=User.Role.BILLER, first_name="Bob", last_name="Cash")

        # 2. Facility & Specialty
        self.facility = Facility.objects.create(
            name="St. Jude Memorial Hospital",
            facility_code="HS-SJM-01",
            facility_type=Facility.FacilityType.GENERAL_HOSPITAL,
            license_number="HOSP-9901",
            phone="+15551234",
            email="contact@stjude.org",
            address_line_1="100 Medical Plaza",
            city="New York",
            state="NY",
            postal_code="10001"
        )
        self.dept = Department.objects.create(facility=self.facility, name="Cardiology", code="CARD")
        self.spec = Specialty.objects.create(name="Cardiovascular Medicine", code="CARD-01")
        self.doctor = DoctorProfile.objects.create(
            user=self.doc_user,
            npi_number="1998822334",
            license_number="MD-NY-8821",
            license_expiry_date=date(2028, 12, 31)
        )
        DoctorSpecialty.objects.create(doctor=self.doctor, specialty=self.spec, is_primary=True)
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
            notes="Admitted via triage"
        )
        self.assertAlmostEqual(float(vitals.bmi), 26.04, places=1)
        self.assertAlmostEqual(float(vitals.calculate_mean_arterial_pressure()), 109.67, places=1)

        # Step 2: Book Doctor Appointment
        appointment = Appointment.objects.create(
            appointment_number="APT-E2E-001",
            patient=self.patient,
            doctor=self.doctor,
            facility=self.facility,
            scheduled_datetime=timezone.now() + timedelta(hours=1),
            duration_minutes=30,
            chief_complaint="Severe recurring hypertension & exertional chest discomfort",
            status=Appointment.Status.CHECKED_IN
        )
        self.assertEqual(appointment.status, Appointment.Status.CHECKED_IN)

        # Step 3: Clinical Encounter & Structured SOAP Note
        encounter = Encounter.objects.create(
            encounter_number="ENC-E2E-001",
            patient=self.patient,
            doctor=self.doctor,
            facility=self.facility,
            encounter_class=Encounter.EncounterClass.AMBULATORY,
            status=Encounter.EncounterStatus.IN_PROGRESS
        )
        dx_code = ICD10DiagnosisCode.objects.create(code="I10", description="Essential (primary) hypertension")
        diag = EncounterDiagnosis.objects.create(encounter=encounter, icd10=dx_code, diagnosis_type=EncounterDiagnosis.DiagnosisType.PRIMARY)
        self.assertEqual(diag.icd10.code, "I10")

        soap = SOAPNote.objects.create(
            encounter=encounter,
            subjective="Patient reports intermittent retrosternal chest tightness lasting 10 minutes on exertion.",
            objective="BP 145/92 mmHg, S1/S2 distinct, no peripheral edema. Lungs clear.",
            assessment="Stage 2 Primary Essential Hypertension, rule out CAD.",
            plan="Initiate Amlodipine 5mg daily. Order Serum Electrolytes & Troponin-I. Lifestyle modification."
        )
        soap.sign_note()
        self.assertTrue(soap.is_signed)
        self.assertIsNotNone(soap.signed_at)

        # Step 4: Diagnostic Laboratory Orders & Pathology Sign-off
        specimen_type = SpecimenType.objects.create(name="Serum Blood", code="BLD-SRM", container_type="Red Top (Serum)")
        lab_test = LabTestCatalog.objects.create(
            loinc_code="49563-0",
            test_name="Troponin-I High Sensitivity",
            category=LabTestCatalog.Category.BIOCHEMISTRY,
            specimen_type=specimen_type,
            measurement_unit="ng/mL",
            standard_cost=Decimal("45.00")
        )
        DemographicReferenceRange.objects.create(
            test=lab_test,
            normal_min=Decimal("0.00"),
            normal_max=Decimal("0.04"),
            critical_high=Decimal("0.10")
        )
        lab_order = LabOrder.objects.create(
            order_number="LAB-ORD-9901",
            patient=self.patient,
            encounter=encounter,
            ordering_doctor=self.doctor,
            priority=LabOrder.OrderPriority.STAT
        )
        res_item = LabResultItem.objects.create(
            order=lab_order,
            test=lab_test,
            observed_numeric_value=Decimal("0.02")
        )
        self.assertEqual(res_item.flag, LabResultItem.Flag.NORMAL)

        # Step 5: Electronic Prescription & Pharmacy Dispensation
        prescription = Prescription.objects.create(
            rx_number="RX-E2E-9901",
            patient=self.patient,
            doctor=self.doctor,
            encounter=encounter,
            expires_at=timezone.now().date() + timedelta(days=90)
        )
        med = Medication.objects.create(brand_name="Norvasc", generic_name="Amlodipine Besylate", strength="5mg", atc_code="C08CA01")
        batch = BatchInventory.objects.create(
            medication=med,
            batch_number="BAT-NORV-001",
            manufacturing_date=timezone.now().date() - timedelta(days=30),
            expiry_date=timezone.now().date() + timedelta(days=365),
            quantity_received=500,
            quantity_on_hand=500,
            cost_per_unit=Decimal("0.25")
            
        )
        rx_item = PrescriptionItem.objects.create(
            prescription=prescription,
            medication_name=med.brand_name,
            dosage="5mg",
            route=PrescriptionItem.Route.ORAL,
            frequency=PrescriptionItem.Frequency.QD,
            duration_days=30,
            quantity=30
        )
        self.assertEqual(len(prescription.signature_hash), 64)

        # Dispense at Pharmacy
        batch.quantity_on_hand -= rx_item.quantity
        batch.save()
        DispensationRecord.objects.create(batch=batch, rx_item_id=rx_item.id, quantity_dispensed=30)
        batch.refresh_from_db()
        self.assertEqual(batch.quantity_on_hand, 470)

        # Step 6: Billing & Invoicing
        fee_consult = FeeSchedule.objects.create(code="99214", description="Specialist Consultation Level 4", base_price=Decimal("150.00"))
        fee_lab = FeeSchedule.objects.create(code="84484", description="Troponin-I High Sensitivity", base_price=Decimal("45.00"))
        fee_pharm = FeeSchedule.objects.create(code="PHARM-01", description="Amlodipine Besylate 5mg", base_price=Decimal("36.00"))

        invoice = Invoice.objects.create(
            invoice_number="INV-E2E-9901",
            patient=self.patient,
            encounter=encounter,
            due_date=timezone.now().date() + timedelta(days=30)
        )
        InvoiceItem.objects.create(invoice=invoice, fee_schedule=fee_consult, item_description=fee_consult.description, quantity=1, unit_price=fee_consult.base_price)
        InvoiceItem.objects.create(invoice=invoice, fee_schedule=fee_lab, item_description=fee_lab.description, quantity=1, unit_price=fee_lab.base_price)
        InvoiceItem.objects.create(invoice=invoice, fee_schedule=fee_pharm, item_description=fee_pharm.description, quantity=1, unit_price=fee_pharm.base_price)
        invoice.calculate_totals()
        self.assertEqual(invoice.total_amount, Decimal("231.00"))

        # Step 7: Insurance Adjudication & Payment Settlement
        payor = InsuranceProvider.objects.create(name="Aetna Global Health", payor_id="AETNA-001", claims_email="claims@aetna.com", claims_phone="+1800111222", address="Aetna Way")
        policy = PatientInsurancePolicy.objects.create(
            patient=self.patient,
            provider=payor,
            policy_number="POL-AET-994",
            copay_amount=Decimal("30.00"),
            effective_start_date=timezone.now().date() - timedelta(days=60),
            effective_end_date=timezone.now().date() + timedelta(days=300)
        )
        claim = InsuranceClaim.objects.create(
            claim_number="CLM-E2E-9901",
            policy=policy,
            invoice=invoice,
            claimed_amount=invoice.total_amount,
            primary_diagnosis_code="I10"
        )
        ClaimAdjudicationService.adjudicate_claim(claim, approved_rate_percent=80.0)
        self.assertEqual(claim.status, InsuranceClaim.ClaimStatus.APPROVED)
        self.assertEqual(claim.approved_amount, Decimal("184.80"))
        self.assertEqual(claim.copay_collected, Decimal("30.00"))

        # Step 8: Patient Co-Pay Settlement
        Payment.objects.create(
            payment_reference="PAY-E2E-0091",
            invoice=invoice,
            amount=Decimal("46.20"),
            payment_method=Payment.PaymentMethod.CREDIT_CARD
        )
        invoice.amount_paid = Decimal("46.20")
        invoice.save()
        invoice.refresh_from_db()
        self.assertEqual(invoice.amount_paid, Decimal("46.20"))
        self.assertEqual(invoice.balance_due, Decimal("184.80"))
