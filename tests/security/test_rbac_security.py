from django.test import TestCase, Client
from apps.accounts.models import User
from apps.patients.models import PatientProfile
from apps.audit.models import AuditLog

class RBACSecurityPolicyTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.patient_user = User.objects.create_user(email="normal.patient@test.org", password="PatPass123!", role=User.Role.PATIENT)
        self.doctor_user = User.objects.create_user(email="specialist.doctor@test.org", password="DocPass123!", role=User.Role.DOCTOR)
        self.admin_user = User.objects.create_user(email="compliance.admin@test.org", password="AdminPass123!", role=User.Role.ADMIN, is_superuser=True)
        self.patient = PatientProfile.objects.create(user=self.patient_user)

    def test_unauthorized_audit_ledger_access_forbidden(self):
        # Patient cannot access HIPAA audit search ledger
        self.client.force_login(self.patient_user)
        resp = self.client.get('/audit/search/')
        self.assertEqual(resp.status_code, 302) # Redirected / unauthorized

    def test_compliance_officer_can_access_audit_ledger(self):
        self.client.force_login(self.admin_user)
        resp = self.client.get('/audit/search/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "HIPAA Security Rule Compliance Audit Ledger")

    def test_audit_log_hash_chain_tamper_detection(self):
        from apps.audit.services import AuditService
        AuditLog.objects.all().delete()
        log1 = AuditService.log_action(actor=self.admin_user, action=AuditLog.Action.CREATE, resource=self.patient)
        log2 = AuditService.log_action(actor=self.admin_user, action=AuditLog.Action.READ, resource=self.patient)
        
        status = AuditService.verify_chain_integrity()
        self.assertTrue(status["is_valid"])

        # Tamper with log1
        AuditLog.objects.filter(id=log1.id).update(changes_json={"tampered": True})
        status_tampered = AuditService.verify_chain_integrity()
        self.assertFalse(status_tampered["is_valid"])
