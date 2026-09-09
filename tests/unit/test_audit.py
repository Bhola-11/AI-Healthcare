from django.test import TestCase
from apps.audit.models import AuditLog
from apps.audit.services import AuditService

class AuditTestCase(TestCase):
    def test_audit_integrity(self):
        log1 = AuditService.log_event("CREATE", "Initial test record", target_model="User", target_id="1")
        log2 = AuditService.log_event("UPDATE", "Updated test record", target_model="User", target_id="1")
        valid, violations = AuditService.verify_trail_integrity()
        self.assertTrue(valid)
        self.assertEqual(log2.previous_hash, log1.integrity_hash)
