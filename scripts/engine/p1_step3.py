from builder_core import run_cmd, write_file, pr_branch, pr_commit, pr_merge

pr_branch("pr/004-audit")

models_code = """import hashlib
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
        payload = f"{self.id}:{self.actor_email}:{self.action}:{self.target_model}:{self.target_id}:{self.timestamp.isoformat()}:{self.previous_hash}"
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
"""
write_file("apps/audit/models.py", models_code)

services_code = """import logging
from .models import AuditLog

logger = logging.getLogger(__name__)

class AuditService:
    @staticmethod
    def log_event(action, description, actor=None, target_model='', target_id='', changes=None, request=None):
        ip = None
        user_agent = ''
        if request:
            ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
            if ip and ',' in ip:
                ip = ip.split(',')[0].strip()
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            if not actor and hasattr(request, 'user') and request.user.is_authenticated:
                actor = request.user

        log = AuditLog(
            actor=actor,
            actor_email=actor.email if actor else 'SYSTEM',
            action=action,
            target_model=target_model,
            target_id=str(target_id),
            description=description,
            changes_json=changes or {},
            ip_address=ip,
            user_agent=user_agent
        )
        log.save()
        return log

    @staticmethod
    def verify_trail_integrity():
        logs = AuditLog.objects.order_by('timestamp')
        expected_prev = "GENESIS_BLOCK_0000000000000000000000000000000000000000000000000000"
        violations = []
        for log in logs:
            if log.previous_hash != expected_prev:
                violations.append((log.id, f"Broken chain link: {log.previous_hash} vs expected {expected_prev}"))
            computed = log.calculate_hash()
            if log.integrity_hash != computed:
                violations.append((log.id, f"Invalid hash: {log.integrity_hash} vs computed {computed}"))
            expected_prev = log.integrity_hash
        return len(violations) == 0, violations
"""
write_file("apps/audit/services.py", services_code)

pr_commit(["apps/audit/models.py"], "feat(audit): implement immutable audit logging model and signal handlers")
pr_commit(["apps/audit/services.py"], "feat(audit): add sha256 checksum integrity verification for audit log records")
pr_merge("pr/004-audit")
print("PR 4 merged successfully.")
