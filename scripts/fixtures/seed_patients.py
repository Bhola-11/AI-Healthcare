import os
import sys
from pathlib import Path
from datetime import date

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
import django
django.setup()

from apps.accounts.models import User
from apps.patients.models import PatientProfile, Allergy, VitalSign, EmergencyContact

def seed():
    data = [
        ("clara.oswald@example.com", "Clara", "Oswald", date(1992, 11, 23), "FEMALE", PatientProfile.BloodGroup.A_POS, "Penicillin", Allergy.Severity.SEVERE),
        ("rory.williams@example.com", "Rory", "Williams", date(1989, 4, 15), "MALE", PatientProfile.BloodGroup.O_POS, "Peanuts", Allergy.Severity.MODERATE),
        ("amy.pond@example.com", "Amy", "Pond", date(1990, 8, 20), "FEMALE", PatientProfile.BloodGroup.B_POS, "Sulfa Drugs", Allergy.Severity.MILD),
        ("rose.tyler@example.com", "Rose", "Tyler", date(1994, 2, 10), "FEMALE", PatientProfile.BloodGroup.AB_POS, "Aspirin", Allergy.Severity.MODERATE),
    ]

    for email, fn, ln, dob, gen, bg, allergen, sev in data:
        user, _ = User.objects.get_or_create(
            email=email,
            defaults={'first_name': fn, 'last_name': ln, 'role': User.Role.PATIENT}
        )
        if _:
            user.set_password("PatientPass123!")
            user.save()

        patient, _ = PatientProfile.objects.get_or_create(
            user=user,
            defaults={'date_of_birth': dob, 'gender': gen, 'blood_group': bg}
        )

        Allergy.objects.get_or_create(
            patient=patient, allergen_name=allergen,
            defaults={'severity': sev, 'reaction_description': f"Acute reaction upon exposure to {allergen}"}
        )

        VitalSign.objects.get_or_create(
            patient=patient, systolic_bp=120, diastolic_bp=80, heart_rate=72,
            defaults={'respiratory_rate': 16, 'temperature_celsius': 36.8, 'spo2_percentage': 99, 'weight_kg': 68.0, 'height_cm': 170.0}
        )

        EmergencyContact.objects.get_or_create(
            patient=patient, name="Guardian Contact", relationship="SPOUSE",
            defaults={'phone_number': '+1555987654', 'email': 'guardian@example.com'}
        )

    print("Patients, allergies, vitals, and emergency contacts seeded.")

if __name__ == '__main__':
    seed()
