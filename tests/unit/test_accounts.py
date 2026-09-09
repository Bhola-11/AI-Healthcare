from django.test import TestCase
from apps.accounts.models import User
from apps.accounts.utils import generate_medical_record_number

class AccountsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="dr.smith@hospital.org",
            password="StrongPassword123!",
            first_name="John",
            last_name="Smith",
            role=User.Role.DOCTOR
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, "dr.smith@hospital.org")
        self.assertTrue(self.user.is_doctor)
        self.assertEqual(self.user.get_full_name(), "John Smith")

    def test_mrn_generator(self):
        mrn = generate_medical_record_number()
        self.assertTrue(mrn.startswith("MRN-"))
        self.assertEqual(len(mrn), 12)
