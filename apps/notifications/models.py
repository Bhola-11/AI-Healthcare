import uuid
from django.db import models
from django.utils import timezone
from apps.accounts.models import User


class Notification(models.Model):
    class Channel(models.TextChoices):
        IN_APP = "IN_APP", "In-App Notification"
        EMAIL = "EMAIL", "Email Alert"
        SMS = "SMS", "SMS Message"

    class Priority(models.TextChoices):
        ROUTINE = "ROUTINE", "Routine Notice"
        IMPORTANT = "IMPORTANT", "Important Notification"
        URGENT = "URGENT", "Urgent Clinical Alert"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=255)
    body = models.TextField()
    channel = models.CharField(max_length=16, choices=Channel.choices, default=Channel.IN_APP)
    priority = models.CharField(max_length=16, choices=Priority.choices, default=Priority.ROUTINE)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    action_url = models.CharField(max_length=512, blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = "hs_notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} to {self.recipient.email} ({self.priority})"

    def mark_as_read(self):
        self.is_read = True
        self.read_at = timezone.now()
        self.save()
