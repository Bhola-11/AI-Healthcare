"""
User and Authentication models for HealthSphere.
Compliant with HIPAA/GDPR standards for healthcare role-based access.
"""
import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom user manager supporting email-based authentication."""
    
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
    """
    Primary User model for HealthSphere healthcare platform.
    Uses UUID4 primary keys and granular healthcare roles.
    """
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
    phone_number = models.CharField(max_length=32, blank=True)
    role = models.CharField(max_length=32, choices=Role.choices, default=Role.PATIENT, db_index=True)
    
    # Status and Security flags
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    
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
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.email

    def get_short_name(self):
        return self.first_name if self.first_name else self.email.split("@")[0]

    @property
    def is_doctor(self):
        return self.role == self.Role.DOCTOR

    @property
    def is_patient(self):
        return self.role == self.Role.PATIENT

    @property
    def is_nurse(self):
        return self.role == self.Role.NURSE

    @property
    def is_pharmacist(self):
        return self.role == self.Role.PHARMACIST

    @property
    def is_lab_technician(self):
        return self.role == self.Role.LAB_TECH

    @property
    def is_billing_officer(self):
        return self.role == self.Role.BILLER

    @property
    def is_receptionist(self):
        return self.role == self.Role.RECEPTIONIST
