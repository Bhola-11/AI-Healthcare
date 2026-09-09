import os
import sys
from pathlib import Path
from datetime import date, time

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
import django
django.setup()

from apps.accounts.models import User
from apps.facilities.models import Facility
from apps.doctors.models import DoctorProfile, Specialty, DoctorSpecialty, DoctorSchedule

def seed():
    specialties_data = [
        ("Cardiology", "CARD", "Diseases of the cardiovascular system, heart failure, arrhythmias"),
        ("Neurology", "NEUR", "Disorders of the nervous system, brain, and spinal cord"),
        ("Oncology", "ONC", "Diagnosis and treatment of benign and malignant tumors"),
        ("Pediatrics", "PED", "Medical care of infants, children, and adolescents"),
        ("Orthopedic Surgery", "ORTH", "Surgical and nonsurgical treatment of musculoskeletal trauma"),
        ("Emergency Medicine", "EM", "Acute resuscitation and stabilization of urgent illnesses"),
        ("Internal Medicine", "IM", "Comprehensive adult multi-system disease management"),
    ]
    for name, code, desc in specialties_data:
        Specialty.objects.get_or_create(code=code, defaults={'name': name, 'description': desc})

    facility = Facility.objects.first()
    if not facility:
        return

    doc_data = [
        ("dr.carter@healthsphere.org", "John", "Carter", "1098765432", "LIC-NY-101", "CARD", 12, 200.00),
        ("dr.meredith@healthsphere.org", "Meredith", "Grey", "1098765433", "LIC-NY-102", "IM", 15, 180.00),
        ("dr.house@healthsphere.org", "Gregory", "House", "1098765434", "LIC-NY-103", "NEUR", 22, 250.00),
    ]

    for email, fn, ln, npi, lic, spec_code, exp, fee in doc_data:
        user, _ = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': fn,
                'last_name': ln,
                'role': User.Role.DOCTOR
            }
        )
        if _:
            user.set_password("DoctorPass123!")
            user.save()

        profile, _ = DoctorProfile.objects.get_or_create(
            user=user,
            defaults={
                'npi_number': npi,
                'license_number': lic,
                'license_expiry_date': date(2028, 6, 30),
                'years_of_experience': exp,
                'default_consultation_fee': fee
            }
        )
        spec = Specialty.objects.get(code=spec_code)
        DoctorSpecialty.objects.get_or_create(doctor=profile, specialty=spec, defaults={'is_primary': True})
        
        # Schedules Monday-Friday
        for dow in range(5):
            DoctorSchedule.objects.get_or_create(
                doctor=profile, facility=facility, day_of_week=dow,
                defaults={'start_time': time(9, 0), 'end_time': time(17, 0)}
            )

    print("Specialties, doctors, and schedules seeded.")

if __name__ == '__main__':
    seed()
