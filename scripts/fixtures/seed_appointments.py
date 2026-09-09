import os
import sys
from pathlib import Path
from datetime import timedelta
from django.utils import timezone

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
import django
django.setup()

from apps.facilities.models import Facility
from apps.doctors.models import DoctorProfile
from apps.patients.models import PatientProfile
from apps.appointments.models import Appointment, QueueTicket

def seed():
    facility = Facility.objects.first()
    doctor = DoctorProfile.objects.first()
    patient = PatientProfile.objects.first()

    if not (facility and doctor and patient):
        return

    now = timezone.now()
    complaints = [
        "Persistent dry cough, mild low-grade fever for 3 days",
        "Routine diabetic glycemic control review and A1C follow-up",
        "Hypertension management and anti-hypertensive titration",
        "Acute left knee pain following sports strain"
    ]

    for i, c in enumerate(complaints):
        dt = now + timedelta(days=i+1, hours=i)
        appt_num = f"APT-DEMO-{1000+i}"
        appt, _ = Appointment.objects.get_or_create(
            appointment_number=appt_num,
            defaults={
                'patient': patient,
                'doctor': doctor,
                'facility': facility,
                'scheduled_datetime': dt,
                'chief_complaint': c,
                'status': Appointment.Status.SCHEDULED if i > 0 else Appointment.Status.CHECKED_IN
            }
        )
        if i == 0:
            QueueTicket.objects.get_or_create(
                appointment=appt,
                defaults={'token_number': 'Q-001'}
            )

    print("Sample appointments and queue ticket seeded.")

if __name__ == '__main__':
    seed()
