import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
import django
django.setup()

from apps.facilities.models import Facility, Department, Ward, Room, Bed

def seed_facilities():
    hospitals = [
        ("HealthSphere Memorial Hospital", "HS-MEM-001", "LIC-HSP-9901", "New York", "NY", 250, Facility.FacilityType.GENERAL_HOSPITAL),
        ("St. Jude Specialty Surgical Center", "HS-SJD-002", "LIC-HSP-9902", "Boston", "MA", 80, Facility.FacilityType.SPECIALTY_CLINIC),
        ("Westside Pediatric & Family Health", "HS-WPF-003", "LIC-HSP-9903", "Chicago", "IL", 60, Facility.FacilityType.COMMUNITY_HEALTH),
    ]
    
    for name, code, lic, city, st, cap, ftype in hospitals:
        fac, _ = Facility.objects.get_or_create(
            facility_code=code,
            defaults={
                'name': name,
                'license_number': lic,
                'city': city,
                'state': st,
                'postal_code': '10001',
                'phone': '+1555123456',
                'email': f"admin@{code.lower()}.org",
                'address_line_1': '1 Healthcare Plaza',
                'total_capacity': cap,
                'facility_type': ftype
            }
        )
        
        depts = [
            ("Emergency Medicine", "EM-01", Department.DepartmentCategory.EMERGENCY, "1"),
            ("Internal Medicine", "IM-01", Department.DepartmentCategory.CLINICAL, "2"),
            ("General Surgery", "GS-01", Department.DepartmentCategory.SURGICAL, "3"),
            ("Cardiology", "CARD-01", Department.DepartmentCategory.CLINICAL, "4"),
            ("Pathology & Diagnostics", "PATH-01", Department.DepartmentCategory.DIAGNOSTIC, "B1"),
        ]
        for dname, dcode, dcat, floor in depts:
            dept, _ = Department.objects.get_or_create(
                facility=fac, code=dcode,
                defaults={'name': dname, 'category': dcat, 'floor_number': floor}
            )
            
            if dcat in [Department.DepartmentCategory.EMERGENCY, Department.DepartmentCategory.CLINICAL]:
                ward, _ = Ward.objects.get_or_create(
                    department=dept, name=f"{dname} Inpatient Ward",
                    defaults={'ward_type': Ward.WardType.ICU if 'Emergency' in dname else Ward.WardType.GENERAL_MALE}
                )
                for r_idx in range(1, 4):
                    room, _ = Room.objects.get_or_create(
                        ward=ward, room_number=f"{floor}0{r_idx}",
                        defaults={'daily_rate': 250.00 if 'ICU' in ward.name else 120.00}
                    )
                    for b_idx in ['A', 'B']:
                        Bed.objects.get_or_create(
                            room=room, bed_identifier=f"Bed-{b_idx}",
                            defaults={'status': Bed.Status.AVAILABLE if b_idx == 'A' else Bed.Status.OCCUPIED}
                        )

    print("Facilities, departments, wards, rooms, and beds seeded successfully.")

if __name__ == '__main__':
    seed_facilities()
