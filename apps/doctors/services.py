from datetime import datetime
from .models import DoctorSchedule, DoctorLeave

class DoctorScheduleConflictService:
    @staticmethod
    def has_leave_conflict(doctor, target_date):
        return DoctorLeave.objects.filter(
            doctor=doctor,
            status=DoctorLeave.LeaveStatus.APPROVED,
            start_date__lte=target_date,
            end_date__gte=target_date
        ).exists()

    @staticmethod
    def is_doctor_available_at_time(doctor, target_datetime):
        target_date = target_datetime.date()
        target_time = target_datetime.time()
        
        if DoctorScheduleConflictService.has_leave_conflict(doctor, target_date):
            return False, "Doctor is on approved medical leave."
            
        day_of_week = target_date.weekday()
        schedule = DoctorSchedule.objects.filter(
            doctor=doctor,
            day_of_week=day_of_week,
            is_active=True,
            start_time__lte=target_time,
            end_time__gte=target_time
        ).first()
        
        if not schedule:
            return False, "Doctor has no active rostered shift at this time."
            
        return True, "Doctor is available."
