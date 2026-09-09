import logging
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

    @classmethod
    def verify_chain_integrity(cls):
        valid, violations = cls.verify_trail_integrity()
        total = AuditLog.objects.count()
        first_tampered = violations[0][0] if violations else None
        return {
            "is_valid": valid,
            "total_nodes": total,
            "tampered_record_id": first_tampered,
            "violations": violations
        }

    @classmethod
    def log_action(cls, actor, action, resource, description="", changes=None, request=None):
        target_model = resource.__class__.__name__ if resource else ""
        target_id = str(getattr(resource, "id", getattr(resource, "pk", "")))
        desc = description or f"{action} performed on {target_model} #{target_id}"
        return cls.log_event(
            action=action,
            description=desc,
            actor=actor,
            target_model=target_model,
            target_id=target_id,
            changes=changes,
            request=request
        )
