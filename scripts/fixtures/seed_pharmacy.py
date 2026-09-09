import os
import sys
from pathlib import Path
from datetime import date, timedelta
from django.utils import timezone

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
import django
django.setup()

from apps.pharmacy.models import Medication, BatchInventory
from apps.prescriptions.models import Prescription, PrescriptionItem
from apps.patients.models import PatientProfile
from apps.doctors.models import DoctorProfile

def seed():
    meds_data = [
        ("Amoxil", "Amoxicillin", "J01CA04", "Beta-lactam Antibiotic", Medication.Form.CAPSULE, "500 mg", 12.50, True),
        ("Lipitor", "Atorvastatin", "C10AA05", "HMG-CoA Reductase Inhibitor", Medication.Form.TABLET, "20 mg", 25.00, False),
        ("Norvasc", "Amlodipine Besylate", "C08CA01", "Dihydropyridine CCB", Medication.Form.TABLET, "5 mg", 15.00, False),
        ("Glucophage", "Metformin Hydrochloride", "A10BA02", "Biguanide Antidiabetic", Medication.Form.TABLET, "850 mg", 8.00, False),
        ("Zestril", "Lisinopril", "C09AA03", "ACE Inhibitor", Medication.Form.TABLET, "10 mg", 14.00, False),
        ("Ventolin", "Albuterol Sulfate", "R03AC02", "Short-acting Beta-2 Agonist", Medication.Form.INHALER, "90 mcg/act", 45.00, False),
        ("Prilosec", "Omeprazole", "A02BC01", "Proton Pump Inhibitor", Medication.Form.CAPSULE, "20 mg", 18.00, False),
        ("Lasix", "Furosemide", "C03CA01", "Loop Diuretic", Medication.Form.TABLET, "40 mg", 9.50, False),
    ]

    for brand, generic, atc, dclass, dform, strength, price, is_antibiotic in meds_data:
        med, _ = Medication.objects.get_or_create(
            atc_code=atc,
            defaults={
                'brand_name': brand,
                'generic_name': generic,
                'drug_class': dclass,
                'dosage_form': dform,
                'strength': strength,
                'unit_price': price,
                'is_antibiotic': is_antibiotic
            }
        )
        BatchInventory.objects.get_or_create(
            medication=med,
            batch_number=f"LOT-{atc[:4]}-2026",
            defaults={
                'manufacturing_date': date(2025, 6, 1),
                'expiry_date': date(2027, 6, 1),
                'quantity_received': 1000,
                'quantity_on_hand': 850,
                'reorder_level': 100
            }
        )

    print("Medications formulary and inventory batches seeded.")

if __name__ == '__main__':
    seed()
