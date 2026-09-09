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

from apps.analytics.models import HospitalKPIReport

def seed():
    HospitalKPIReport.objects.get_or_create(
        report_date=date(2026, 9, 8),
        defaults={
            'total_admissions': 18,
            'total_discharges': 15,
            'bed_occupancy_rate': Decimal("82.50"),
            'average_length_of_stay_days': Decimal("3.4"),
            'daily_revenue': Decimal("45000.00"),
            'claim_denial_rate': Decimal("1.80")
        }
    )
    print("Analytics KPI report seeded.")

if __name__ == '__main__':
    seed()
