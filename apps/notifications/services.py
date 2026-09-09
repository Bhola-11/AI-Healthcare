from .models import Notification

class NotificationService:
    @staticmethod
    def send(recipient, title, body, channel=Notification.Channel.IN_APP, priority=Notification.Priority.ROUTINE, action_url=''):
        return Notification.objects.create(
            recipient=recipient,
            title=title,
            body=body,
            channel=channel,
            priority=priority,
            action_url=action_url
        )
