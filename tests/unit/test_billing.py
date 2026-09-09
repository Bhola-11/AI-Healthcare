from datetime import date
from decimal import Decimal
from django.test import TestCase
from apps.accounts.models import User
from apps.patients.models import PatientProfile
from apps.billing.models import FeeSchedule, Invoice, InvoiceItem, Payment
from apps.insurance.models import InsuranceProvider, PatientInsurancePolicy, InsuranceClaim
from apps.insurance.services import ClaimAdjudicationService

class BillingTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="pat.bill@test.org", password="Pass123!", role=User.Role.PATIENT)
        self.patient = PatientProfile.objects.create(user=self.user)
        self.fee = FeeSchedule.objects.create(code="99213", description="Office Visit Level 3", base_price=Decimal("120.00"))
        self.provider = InsuranceProvider.objects.create(name="Blue Cross Blue Shield", payor_id="BCBS-01", claims_email="claims@bcbs.com", claims_phone="123", address="Main St")
        self.policy = PatientInsurancePolicy.objects.create(
            patient=self.patient,
            provider=self.provider,
            policy_number="POL-9999",
            effective_start_date=date(2025, 1, 1),
            effective_end_date=date(2027, 1, 1),
            copay_amount=Decimal("25.00")
        )

    def test_invoice_calculation_and_payment_settlement(self):
        inv = Invoice.objects.create(invoice_number="INV-001", patient=self.patient, due_date=date(2026, 10, 1))
        item = InvoiceItem.objects.create(invoice=inv, fee_schedule=self.fee, item_description=self.fee.description, quantity=1, unit_price=Decimal("120.00"))
        inv.calculate_totals()
        self.assertEqual(inv.total_amount, Decimal("120.00"))
        self.assertEqual(inv.balance_due, Decimal("120.00"))

        # Pay full
        pay = Payment.objects.create(payment_reference="PAY-001", invoice=inv, amount=Decimal("120.00"))
        inv.refresh_from_db()
        self.assertEqual(inv.status, Invoice.Status.PAID)
        self.assertEqual(inv.balance_due, Decimal("0.00"))

    def test_claim_adjudication(self):
        inv = Invoice.objects.create(invoice_number="INV-CLM-01", patient=self.patient, due_date=date(2026, 10, 1), total_amount=Decimal("500.00"))
        claim = InsuranceClaim.objects.create(
            claim_number="CLM-001",
            policy=self.policy,
            invoice=inv,
            claimed_amount=Decimal("500.00"),
            primary_diagnosis_code="I10"
        )
        ClaimAdjudicationService.adjudicate_claim(claim, approved_rate_percent=80.0)
        self.assertEqual(claim.status, InsuranceClaim.ClaimStatus.APPROVED)
        self.assertEqual(claim.approved_amount, Decimal("400.00"))
        self.assertEqual(claim.copay_collected, Decimal("25.00"))
