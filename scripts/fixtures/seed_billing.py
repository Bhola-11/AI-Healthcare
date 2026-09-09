import os
import sys
from pathlib import Path
from decimal import Decimal
from datetime import date

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
import django
django.setup()

from apps.billing.models import FeeSchedule, Invoice, InvoiceItem, Payment
from apps.insurance.models import InsuranceProvider, PatientInsurancePolicy
from apps.patients.models import PatientProfile

def seed():
    fees = [
        ("99203", "Office/Outpatient New Patient 30 min", FeeSchedule.ServiceCategory.CONSULTATION, "150.00"),
        ("99214", "Office/Outpatient Established Patient 25 min", FeeSchedule.ServiceCategory.CONSULTATION, "110.00"),
        ("99284", "Emergency Department Visit High Severity", FeeSchedule.ServiceCategory.EMERGENCY_FEE, "450.00"),
        ("80053", "Comprehensive Metabolic Panel (CMP)", FeeSchedule.ServiceCategory.DIAGNOSTIC_LAB, "65.00"),
        ("85025", "Complete Blood Count (CBC) with Differential", FeeSchedule.ServiceCategory.DIAGNOSTIC_LAB, "40.00"),
        ("71045", "Chest X-Ray Single View", FeeSchedule.ServiceCategory.RADIOLOGY, "95.00"),
        ("93000", "Electrocardiogram (ECG/EKG) 12-lead", FeeSchedule.ServiceCategory.RADIOLOGY, "75.00"),
    ]
    for code, desc, cat, price in fees:
        FeeSchedule.objects.get_or_create(code=code, defaults={'description': desc, 'category': cat, 'base_price': Decimal(price)})

    providers = [
        ("UnitedHealthcare", "UHC-001", "Commercial"),
        ("Aetna Health", "AETNA-002", "Commercial"),
        ("Medicare Part B", "MED-003", "Federal"),
    ]
    for name, pid, ptype in providers:
        InsuranceProvider.objects.get_or_create(
            payor_id=pid,
            defaults={'name': name, 'claims_email': f"claims@{pid.lower()}.com", 'claims_phone': '+18005550199', 'address': '100 Corporate Pkwy'}
        )

    print("Fee schedules and insurance providers master seeded.")

if __name__ == '__main__':
    seed()
