from apps.notifications.services import NotificationService
from apps.notifications.models import Notification
from .models import LabResultItem

class CriticalLabAlertService:
    @staticmethod
    def notify_critical_result(result_item):
        if result_item.flag in [LabResultItem.Flag.CRITICAL_HIGH, LabResultItem.Flag.CRITICAL_LOW]:
            doctor_user = result_item.order.ordering_doctor.user
            NotificationService.send(
                recipient=doctor_user,
                title="PANIC / CRITICAL VALUE LABORATORY ALERT",
                body=f"URGENT: Patient {result_item.order.patient.user.get_full_name()} (MRN: {result_item.order.patient.mrn}) has a critical lab threshold: {result_item.test.test_name} = {result_item.observed_numeric_value} {result_item.test.measurement_unit} ({result_item.get_flag_display()}). Immediate intervention required.",
                channel=Notification.Channel.IN_APP,
                priority=Notification.Priority.URGENT
            )
            return True
        return False
