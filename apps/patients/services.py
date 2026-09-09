from .models import VitalSign

class VitalsAnalyticsService:
    @staticmethod
    def get_vitals_trend_series(patient_id, count=15):
        vitals = VitalSign.objects.filter(patient_id=patient_id).order_by('recorded_at')[:count]
        dates = [v.recorded_at.strftime('%m/%d %H:%M') for v in vitals]
        systolic = [v.systolic_bp for v in vitals]
        diastolic = [v.diastolic_bp for v in vitals]
        heart_rate = [v.heart_rate for v in vitals]
        spo2 = [v.spo2_percentage for v in vitals]
        
        return {
            "dates": dates,
            "systolic": systolic,
            "diastolic": diastolic,
            "heart_rate": heart_rate,
            "spo2": spo2
        }
