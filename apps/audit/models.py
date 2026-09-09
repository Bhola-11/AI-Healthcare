import hashlib
import json
import uuid
from django.db import models
from django.utils import timezone
from apps.accounts.models import User


class AuditLog(models.Model):
    class ActionType(models.TextChoices):
        CREATE = "CREATE", "Record Created"
        READ = "READ", "Record Accessed / Viewed"
        UPDATE = "UPDATE", "Record Modified"
        DELETE = "DELETE", "Record Deleted"
        LOGIN = "LOGIN", "User Login"
        LOGOUT = "LOGOUT", "User Logout"
        FAILED_LOGIN = "FAILED_LOGIN", "Failed Authentication Attempt"
        EXPORT = "EXPORT", "PHI Data Exported"
        DISPENSE = "DISPENSE", "Medication Dispensed"
        OVERRIDE = "OVERRIDE", "Clinical Alert Overridden"

    Action = ActionType

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_logs")
    actor_email = models.EmailField(blank=True)
    action = models.CharField(max_length=32, choices=ActionType.choices, db_index=True)
    target_model = models.CharField(max_length=128, db_index=True)
    target_id = models.CharField(max_length=128, db_index=True, blank=True)
    description = models.TextField()
    changes_json = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    
    previous_hash = models.CharField(max_length=64, blank=True)
    integrity_hash = models.CharField(max_length=64, db_index=True)

    class Meta:
        db_table = "hs_audit_logs"
        ordering = ["-timestamp"]

    def calculate_hash(self):
        payload = f"{self.id}:{self.actor_email}:{self.action}:{self.target_model}:{self.target_id}:{self.timestamp.isoformat()}:{json.dumps(self.changes_json, sort_keys=True)}:{self.previous_hash}"
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

    def save(self, *args, **kwargs):
        if self.actor and not self.actor_email:
            self.actor_email = self.actor.email
        if not self.previous_hash:
            last_log = AuditLog.objects.order_by('-timestamp').first()
            if last_log:
                self.previous_hash = last_log.integrity_hash
            else:
                self.previous_hash = "GENESIS_BLOCK_0000000000000000000000000000000000000000000000000000"
        self.integrity_hash = self.calculate_hash()
        super().save(*args, **kwargs)
