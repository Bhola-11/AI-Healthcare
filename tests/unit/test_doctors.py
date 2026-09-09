from datetime import date, time, datetime
from django.test import TestCase
from apps.accounts.models import User
from apps.facilities.models import Facility
from apps.doctors.models import DoctorProfile, Specialty, DoctorSchedule, DoctorLeave
from apps.doctors.services import DoctorScheduleConflictService

class DoctorTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="dr.wilson@healthsphere.org",
            password="StrongPassword123!",
            first_name="Gregory",
            last_name="Wilson",
            role=User.Role.DOCTOR
        )
        self.facility = Facility.objects.create(
            name="General Hospital",
            facility_code="HS-GEN-02",
            license_number="LIC-GEN-02",
            phone="+15559876",
            email="info@genhosp.org",
            address_line_1="100 Hospital Way",
            city="New York",
            state="NY",
            postal_code="10001"
        )
        self.doctor = DoctorProfile.objects.create(
            user=self.user,
            npi_number="1234567890",
            license_number="MED-LIC-9988",
            license_expiry_date=date(2028, 12, 31)
        )
        self.schedule = DoctorSchedule.objects.create(
            doctor=self.doctor,
            facility=self.facility,
            day_of_week=0, # Monday
            start_time=time(9, 0),
            end_time=time(17, 0)
        )

    def test_schedule_service(self):
        # 2026-09-14 is a Monday
        avail, msg = DoctorScheduleConflictService.is_doctor_available_at_time(
            self.doctor, datetime(2026, 9, 14, 10, 30)
        )
        self.assertTrue(avail, msg)

    def test_leave_conflict(self):
        DoctorLeave.objects.create(
            doctor=self.doctor,
            start_date=date(2026, 9, 14),
            end_date=date(2026, 9, 16),
            reason="Conference",
            status=DoctorLeave.LeaveStatus.APPROVED
        )
        avail, msg = DoctorScheduleConflictService.is_doctor_available_at_time(
            self.doctor, datetime(2026, 9, 14, 10, 30)
        )
        self.assertFalse(avail)
