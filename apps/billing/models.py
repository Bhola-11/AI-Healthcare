import uuid
from decimal import Decimal
from django.db import models
from django.utils import timezone
from apps.patients.models import PatientProfile
from apps.clinical_records.models import Encounter


class FeeSchedule(models.Model):
    class ServiceCategory(models.TextChoices):
        CONSULTATION = "CONSULTATION", "Physician Consultation"
        DIAGNOSTIC_LAB = "DIAGNOSTIC_LAB", "Clinical Laboratory Test"
        RADIOLOGY = "RADIOLOGY", "Radiology / Diagnostic Imaging"
        SURGICAL_PROCEDURE = "SURGICAL_PROCEDURE", "Surgical / Minor Procedure"
        ROOM_BOARD = "ROOM_BOARD", "Inpatient Room & Bed Accommodation"
        PHARMACY = "PHARMACY", "Medication & Biological Supplies"
        EMERGENCY_FEE = "EMERGENCY_FEE", "Emergency Resuscitation & Triage Fee"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=32, unique=True, db_index=True)
    description = models.CharField(max_length=255)
    category = models.CharField(max_length=32, choices=ServiceCategory.choices, default=ServiceCategory.CONSULTATION)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    tax_rate_percent = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "hs_billing_fee_schedules"
        ordering = ["category", "code"]

    def __str__(self):
        return f"{self.code} - {self.description} (${self.base_price})"

class Invoice(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft Pending Finalization"
        ISSUED = "ISSUED", "Issued to Patient / Payor"
        PARTIALLY_PAID = "PARTIALLY_PAID", "Partially Paid"
        PAID = "PAID", "Fully Paid / Settled"
        VOID = "VOID", "Voided / Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=32, unique=True, db_index=True)
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="invoices")
    encounter = models.ForeignKey(Encounter, on_delete=models.SET_NULL, null=True, blank=True, related_name="invoices")
    
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.ISSUED, db_index=True)
    due_date = models.DateField()
    issued_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "hs_billing_invoices"
        ordering = ["-issued_at"]

    @property
    def balance_due(self):
        tot = Decimal(str(self.total_amount or "0.00"))
        paid = Decimal(str(self.amount_paid or "0.00"))
        return tot - paid

    def calculate_totals(self):
        items = list(self.items.all())
        self.subtotal = sum((Decimal(str(it.quantity)) * it.unit_price) for it in items) if items else Decimal("0.00")
        tax = Decimal(str(self.tax_amount or "0.00"))
        discount = Decimal(str(self.discount_amount or "0.00"))
        self.total_amount = self.subtotal + tax - discount
        self.save()

    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.patient.user.get_full_name()} (${self.total_amount})"


class InvoiceItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    fee_schedule = models.ForeignKey(FeeSchedule, on_delete=models.SET_NULL, null=True, blank=True)
    item_description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "hs_billing_invoice_items"

    def save(self, *args, **kwargs):
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)

class Payment(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH = "CASH", "Cash Currency"
        CREDIT_CARD = "CREDIT_CARD", "Credit / Debit Card"
        INSURANCE_COPAY = "INSURANCE_COPAY", "Insurance Co-payment"
        BANK_TRANSFER = "BANK_TRANSFER", "Electronic Bank Wire (ACH)"
        CHECK = "CHECK", "Paper Check"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment_reference = models.CharField(max_length=64, unique=True, db_index=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=32, choices=PaymentMethod.choices, default=PaymentMethod.CREDIT_CARD)
    transaction_id = models.CharField(max_length=128, blank=True)
    received_by = models.CharField(max_length=255, default="Cashier Desk")
    paid_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "hs_billing_payments"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update invoice amount paid
        self.invoice.amount_paid = sum(p.amount for p in self.invoice.payments.all())
        if self.invoice.amount_paid >= self.invoice.total_amount:
            self.invoice.status = Invoice.Status.PAID
        elif self.invoice.amount_paid > 0:
            self.invoice.status = Invoice.Status.PARTIALLY_PAID
        self.invoice.save()

    def __str__(self):
        return f"Payment #{self.payment_reference} (${self.amount}) for Invoice #{self.invoice.invoice_number}"

class PatientLedgerEntry(models.Model):
    class EntryType(models.TextChoices):
        CHARGE = "CHARGE", "Debit / Patient Charge"
        PAYMENT = "PAYMENT", "Credit / Payment Received"
        INSURANCE_CREDIT = "INSURANCE_CREDIT", "Credit / Insurance Adjudication"
        ADJUSTMENT = "ADJUSTMENT", "Administrative Waiver / Adjustment"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name="ledger_entries")
    entry_type = models.CharField(max_length=32, choices=EntryType.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    running_balance = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255)
    reference_number = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "hs_billing_patient_ledger"
        ordering = ["created_at"]
