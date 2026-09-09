import os
import sys
from pathlib import Path
from decimal import Decimal

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
import django
django.setup()

from apps.laboratory.models import SpecimenType, LabTestCatalog, DemographicReferenceRange

def seed():
    specs = [
        ("Serum Blood", "BLD-SER", "Red Top Tube (Clot Activator)"),
        ("Plasma Blood", "BLD-PLA", "Green Top Tube (Lithium Heparin)"),
        ("Whole Blood", "BLD-EDTA", "Lavender Top Tube (K2-EDTA)"),
        ("Clean Catch Urine", "URN-CC", "Sterile Screw-cap Container"),
        ("Nasopharyngeal Swab", "SWB-NP", "Viral Transport Media (VTM)"),
    ]
    spec_map = {}
    for name, code, container in specs:
        s, _ = SpecimenType.objects.get_or_create(code=code, defaults={'name': name, 'container_type': container})
        spec_map[code] = s

    tests = [
        ("718-7", "Hemoglobin", LabTestCatalog.Category.HEMATOLOGY, "BLD-EDTA", "g/dL", "12.0", "17.0", "7.0", "20.0"),
        ("6690-2", "Leukocytes (WBC)", LabTestCatalog.Category.HEMATOLOGY, "BLD-EDTA", "10^3/uL", "4.5", "11.0", "2.0", "30.0"),
        ("777-3", "Platelets", LabTestCatalog.Category.HEMATOLOGY, "BLD-EDTA", "10^3/uL", "150", "450", "20", "1000"),
        ("2345-7", "Glucose, Fasting", LabTestCatalog.Category.BIOCHEMISTRY, "BLD-SER", "mg/dL", "70", "99", "40", "400"),
        ("2823-3", "Potassium, Serum", LabTestCatalog.Category.BIOCHEMISTRY, "BLD-SER", "mmol/L", "3.5", "5.0", "2.8", "6.2"),
        ("2951-2", "Sodium, Serum", LabTestCatalog.Category.BIOCHEMISTRY, "BLD-SER", "mmol/L", "135", "145", "120", "160"),
        ("2160-0", "Creatinine, Serum", LabTestCatalog.Category.BIOCHEMISTRY, "BLD-SER", "mg/dL", "0.7", "1.3", "0.3", "5.0"),
        ("17861-6", "Calcium, Total", LabTestCatalog.Category.BIOCHEMISTRY, "BLD-SER", "mg/dL", "8.5", "10.5", "6.5", "13.0"),
        ("49563-0", "Troponin I, High Sensitivity", LabTestCatalog.Category.BIOCHEMISTRY, "BLD-PLA", "ng/L", "0.0", "14.0", "0.0", "50.0"),
        ("4548-4", "Hemoglobin A1c (HbA1c)", LabTestCatalog.Category.ENDOCRINOLOGY, "BLD-EDTA", "%", "4.0", "5.6", "3.0", "14.0"),
    ]

    for loinc, name, cat, scode, unit, nmin, nmax, cmin, cmax in tests:
        test, _ = LabTestCatalog.objects.get_or_create(
            loinc_code=loinc,
            defaults={
                'test_name': name,
                'category': cat,
                'specimen_type': spec_map[scode],
                'measurement_unit': unit,
                'standard_cost': Decimal("45.00")
            }
        )
        DemographicReferenceRange.objects.get_or_create(
            test=test,
            gender="ALL",
            defaults={
                'normal_min': Decimal(nmin),
                'normal_max': Decimal(nmax),
                'critical_low': Decimal(cmin),
                'critical_high': Decimal(cmax)
            }
        )

    print("LOINC diagnostic lab test catalog and reference ranges seeded.")

if __name__ == '__main__':
    seed()
