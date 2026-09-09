import uuid
from decimal import Decimal
from django.db import models
from django.utils import timezone


class HospitalKPIReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_date = models.DateField(unique=True, db_index=True)
    total_admissions = models.PositiveIntegerField(default=0)
    total_discharges = models.PositiveIntegerField(default=0)
    bed_occupancy_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    average_length_of_stay_days = models.DecimalField(max_digits=4, decimal_places=1, default=3.5)
    emergency_wait_time_minutes = models.PositiveIntegerField(default=22)
    daily_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    claim_denial_rate = models.DecimalField(max_digits=5, decimal_places=2, default=2.10)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "hs_analytics_kpi_reports"
        ordering = ["-report_date"]

    def __str__(self):
        return f"KPI Report for {self.report_date} (Occupancy: {self.bed_occupancy_rate}%)"
