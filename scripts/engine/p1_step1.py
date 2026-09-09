from builder_core import run_cmd, write_file, pr_branch, pr_commit, pr_merge

pr_branch("pr/002-accounts")

models_code = """import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.core.validators import RegexValidator


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Healthcare users must have a valid email address.")
        email = self.normalize_email(email).lower()
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.ADMIN)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "System Administrator"
        DOCTOR = "DOCTOR", "Physician / Specialist"
        NURSE = "NURSE", "Registered Nurse"
        PATIENT = "PATIENT", "Patient"
        PHARMACIST = "PHARMACIST", "Pharmacist"
        LAB_TECH = "LAB_TECH", "Laboratory Technician"
        BILLER = "BILLER", "Billing & Insurance Officer"
        RECEPTIONIST = "RECEPTIONIST", "Receptionist / Registrar"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, max_length=255, db_index=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Format: '+999999999'.")
    phone_number = models.CharField(validators=[phone_regex], max_length=32, blank=True)
    role = models.CharField(max_length=32, choices=Role.choices, default=Role.PATIENT, db_index=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    password_changed_at = models.DateTimeField(default=timezone.now)
    
    date_joined = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        db_table = "hs_users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()}) - {self.email}"

    def get_full_name(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return name if name else self.email

    def get_short_name(self):
        return self.first_name if self.first_name else self.email.split("@")[0]

    @property
    def is_doctor(self): return self.role == self.Role.DOCTOR
    @property
    def is_patient(self): return self.role == self.Role.PATIENT
    @property
    def is_nurse(self): return self.role == self.Role.NURSE
    @property
    def is_pharmacist(self): return self.role == self.Role.PHARMACIST
    @property
    def is_lab_technician(self): return self.role == self.Role.LAB_TECH
    @property
    def is_billing_officer(self): return self.role == self.Role.BILLER
    @property
    def is_receptionist(self): return self.role == self.Role.RECEPTIONIST


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=16,
        choices=[("MALE", "Male"), ("FEMALE", "Female"), ("OTHER", "Other"), ("UNDISCLOSED", "Undisclosed")],
        default="UNDISCLOSED"
    )
    national_id = models.CharField(max_length=64, blank=True, db_index=True)
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default="United States")
    bio = models.TextField(blank=True)
    timezone = models.CharField(max_length=64, default="UTC")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hs_user_profiles"

    def __str__(self):
        return f"Profile of {self.user.get_full_name()}"


class PasswordHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="password_history")
    password_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hs_user_password_history"
        ordering = ["-created_at"]
"""
write_file("apps/accounts/models.py", models_code)

validators_code = """import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class HealthcarePasswordValidator:
    def validate(self, password, user=None):
        if len(password) < 8:
            raise ValidationError(_("Healthcare passwords must contain at least 8 characters."))
        if not re.search(r'[A-Z]', password):
            raise ValidationError(_("Password must contain at least one uppercase letter (A-Z)."))
        if not re.search(r'[a-z]', password):
            raise ValidationError(_("Password must contain at least one lowercase letter (a-z)."))
        if not re.search(r'[0-9]', password):
            raise ValidationError(_("Password must contain at least one numeric digit (0-9)."))
        if not re.search(r'[@$!%*?&#^+=~_-]', password):
            raise ValidationError(_("Password must contain at least one special character (@$!%*?&#^+=~_-)."))

    def get_help_text(self):
        return _("Must be at least 8 characters, with uppercase, lowercase, numbers, and special symbols.")
"""
write_file("apps/accounts/validators.py", validators_code)

pr_commit(["apps/accounts/models.py"], "feat(accounts): implement custom user model with email authentication and roles")
pr_commit(["apps/accounts/validators.py"], "feat(accounts): add user profile, credentials validation and password hashing policies")
pr_merge("pr/002-accounts")
print("PR 2 merged successfully.")
