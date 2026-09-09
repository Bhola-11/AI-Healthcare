from django.test import TestCase
from apps.facilities.models import Facility, Department, Ward, Room, Bed
from apps.facilities.services import BedOccupancyService

class FacilitiesTestCase(TestCase):
    def setUp(self):
        self.facility = Facility.objects.create(
            name="General HealthSphere Hospital",
            facility_code="HS-GEN-01",
            license_number="LIC-2026-001",
            phone="+15550199",
            email="general@healthsphere.org",
            address_line_1="100 Medical Blvd",
            city="New York",
            state="NY",
            postal_code="10001",
            total_capacity=50
        )
        self.dept = Department.objects.create(
            facility=self.facility,
            name="Cardiology & Critical Care",
            code="CARD-01"
        )
        self.ward = Ward.objects.create(
            department=self.dept,
            name="Cardiology ICU",
            ward_type=Ward.WardType.ICU
        )
        self.room = Room.objects.create(
            ward=self.ward,
            room_number="ICU-101"
        )
        self.bed1 = Bed.objects.create(room=self.room, bed_identifier="B1", status=Bed.Status.AVAILABLE)
        self.bed2 = Bed.objects.create(room=self.room, bed_identifier="B2", status=Bed.Status.OCCUPIED)

    def test_bed_occupancy_service(self):
        metrics = BedOccupancyService.calculate_facility_occupancy(self.facility.id)
        self.assertEqual(metrics["total"], 2)
        self.assertEqual(metrics["occupied"], 1)
        self.assertEqual(metrics["available"], 1)
        self.assertEqual(metrics["rate"], 50.0)

    def test_find_available_bed(self):
        bed = BedOccupancyService.find_available_bed(self.facility.id, ward_type=Ward.WardType.ICU)
        self.assertIsNotNone(bed)
        self.assertEqual(bed.bed_identifier, "B1")
