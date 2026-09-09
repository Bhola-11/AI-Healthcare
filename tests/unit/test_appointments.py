from datetime import datetime
from django.test import TestCase
from django.utils import timezone
from apps.accounts.models import User
from apps.facilities.models import Facility
from apps.doctors.models import DoctorProfile
from apps.patients.models import PatientProfile
from apps.appointments.models import Appointment, QueueTicket
from apps.appointments.services import AppointmentBookingService

class AppointmentTestCase(TestCase):
    def setUp(self):
        self.doc_user = User.objects.create_user(email="dr.appt@test.org", password="Pass123!", role=User.Role.DOCTOR)
        self.pat_user = User.objects.create_user(email="pat.appt@test.org", password="Pass123!", role=User.Role.PATIENT)
        self.facility = Facility.objects.create(name="Central Clinic", facility_code="CC-01", license_number="L1", phone="123", email="c@c.org", address_line_1="A1", city="C", state="S", postal_code="000")
        self.doctor = DoctorProfile.objects.create(user=self.doc_user, npi_number="9988776655", license_number="L-99", license_expiry_date=datetime(2028, 1, 1).date())
        self.patient = PatientProfile.objects.create(user=self.pat_user)

    def test_slot_booking_and_double_booking_prevention(self):
        dt = timezone.now() + timezone.timedelta(days=2)
        appt = AppointmentBookingService.reserve_slot(
            patient=self.patient,
            doctor=self.doctor,
            facility=self.facility,
            scheduled_datetime=dt,
            chief_complaint="Chest pain and palpitations"
        )
        self.assertEqual(appt.status, Appointment.Status.SCHEDULED)

        # Attempt to double book same slot
        with self.assertRaises(ValueError):
            AppointmentBookingService.reserve_slot(
                patient=self.patient,
                doctor=self.doctor,
                facility=self.facility,
                scheduled_datetime=dt,
                chief_complaint="Second booking attempt"
            )
