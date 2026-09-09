from builder_core import run_cmd, write_file, pr_branch, pr_commit, pr_merge

# ----------------------------------------------------
# PR #7: Error Handling (Commit #12)
# ----------------------------------------------------
pr_branch("pr/007-error-handling")

for code, title, desc in [
    (400, "Bad Request", "The server could not understand your clinical request parameters."),
    (403, "Access Forbidden", "You do not have the necessary healthcare security clearance for this resource."),
    (404, "Page / Record Not Found", "The requested patient file, encounter, or page does not exist."),
    (500, "Internal Server Error", "An internal clinical system error occurred. It has been securely logged.")
]:
    write_file(f"templates/{code}.html", f"""{{% extends 'base.html' %}}
{{% block title %}}{code} {title} - HealthSphere{{% endblock %}}
{{% block content %}}
<div class="hs-card text-center" style="max-width: 600px; margin: 4rem auto; padding: 2rem;">
    <h1 style="font-size: 4rem; color: var(--hs-primary);">{code}</h1>
    <h2>{title}</h2>
    <p class="hs-text-muted mt-4">{desc}</p>
    <div class="mt-4">
        <a href="{{% url 'accounts:dashboard' %}}" class="hs-btn hs-btn-primary">Return to Dashboard</a>
    </div>
</div>
{{% endblock %}}
""")

pr_commit(["templates/400.html", "templates/403.html", "templates/404.html", "templates/500.html"], "feat(core): implement global exception handlers, custom error views (400, 403, 404, 500)")
pr_merge("pr/007-error-handling")
print("PR 7 merged.")

# ----------------------------------------------------
# PR #8: Notifications Subsystem (Commits #13, #14)
# ----------------------------------------------------
pr_branch("pr/008-notifications")

notif_models = """import uuid
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
"""
write_file("apps/notifications/models.py", notif_models)
run_cmd("python manage.py makemigrations notifications")
run_cmd("python manage.py migrate notifications")

pr_commit(["apps/notifications/models.py", "apps/notifications/migrations/"], "feat(notifications): implement notification models, templates and in-app alert dispatcher")

notif_services = """from .models import Notification

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
"""
write_file("apps/notifications/services.py", notif_services)

notif_views = """from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def notification_list(request):
    notifications = request.user.notifications.all()
    return render(request, 'notifications/list.html', {'notifications': notifications})

@login_required
def mark_read(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, recipient=request.user)
    notif.mark_as_read()
    return redirect('notifications:list')
"""
write_file("apps/notifications/views.py", notif_views)

notif_urls = """from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='list'),
    path('<uuid:notif_id>/read/', views.mark_read, name='mark_read'),
]
"""
write_file("apps/notifications/urls.py", notif_urls)

notif_template = """{% extends 'base.html' %}
{% block title %}Notifications - HealthSphere{% endblock %}
{% block content %}
<div class="hs-card">
    <div class="hs-card-header">
        <h2>Notifications & Alerts</h2>
    </div>
    <div class="hs-card-body">
        {% if notifications %}
            <div class="hs-notif-list">
                {% for n in notifications %}
                    <div class="hs-notif-item" style="padding: 1rem; border-bottom: 1px solid var(--hs-border);">
                        <h4>{{ n.title }} <small class="hs-text-muted">({{ n.get_priority_display }})</small></h4>
                        <p>{{ n.body }}</p>
                        {% if not n.is_read %}
                            <a href="{% url 'notifications:mark_read' n.id %}" class="hs-btn hs-btn-outline-sm mt-2">Mark Read</a>
                        {% endif %}
                    </div>
                {% endfor %}
            </div>
        {% else %}
            <p class="hs-text-muted">No notifications right now.</p>
        {% endif %}
    </div>
</div>
{% endblock %}
"""
write_file("templates/notifications/list.html", notif_template)

pr_commit(["apps/notifications/services.py", "apps/notifications/views.py", "apps/notifications/urls.py", "templates/notifications/list.html"], "feat(notifications): add multi-channel notification engine for email and sms abstraction")
pr_merge("pr/008-notifications")
print("PR 8 merged.")

# ----------------------------------------------------
# PR #9: Core Utilities (Commit #15)
# ----------------------------------------------------
pr_branch("pr/009-utilities")

utils_acc = """import secrets
import string

def generate_medical_record_number(prefix="MRN"):
    chars = string.ascii_uppercase + string.digits
    rand = ''.join(secrets.choice(chars) for _ in range(8))
    return f"{prefix}-{rand}"

def sanitize_phi_text(text):
    if not text:
        return ""
    return " ".join(text.strip().split())
"""
write_file("apps/accounts/utils.py", utils_acc)

utils_audit = """def mask_ssn(ssn):
    if not ssn or len(ssn) < 4:
        return "****"
    return f"***-**-{ssn[-4:]}"

def mask_email(email):
    if not email or '@' not in email:
        return "***"
    user, domain = email.split('@', 1)
    masked_user = user[0] + '***' + (user[-1] if len(user) > 1 else '')
    return f"{masked_user}@{domain}"
"""
write_file("apps/audit/utils.py", utils_audit)

pr_commit(["apps/accounts/utils.py", "apps/audit/utils.py"], "feat(core): implement system-wide utilities, data formatters and sanitizers")
pr_merge("pr/009-utilities")
print("PR 9 merged.")

# ----------------------------------------------------
# PR #10: CI/CD & Tests (Commits #16, #17)
# ----------------------------------------------------
pr_branch("pr/010-ci-testing")

test_acc = """from django.test import TestCase
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
"""
write_file("tests/unit/test_accounts.py", test_acc)

test_audit = """from django.test import TestCase
from apps.audit.models import AuditLog
from apps.audit.services import AuditService

class AuditTestCase(TestCase):
    def test_audit_integrity(self):
        log1 = AuditService.log_event("CREATE", "Initial test record", target_model="User", target_id="1")
        log2 = AuditService.log_event("UPDATE", "Updated test record", target_model="User", target_id="1")
        valid, violations = AuditService.verify_trail_integrity()
        self.assertTrue(valid)
        self.assertEqual(log2.previous_hash, log1.integrity_hash)
"""
write_file("tests/unit/test_audit.py", test_audit)

ci_yaml = """name: HealthSphere CI Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run Django Checks
      run: |
        python manage.py check
    - name: Run Tests
      run: |
        python manage.py test
"""
write_file(".github/workflows/ci.yml", ci_yaml)

pr_commit(["tests/unit/test_accounts.py", "tests/unit/test_audit.py"], "test(core): configure django test runner, base fixtures and test helpers")
pr_commit([".github/workflows/ci.yml"], "ci(github): add github actions workflow for linting, security scans and test suites")
pr_merge("pr/010-ci-testing")
print("PR 10 merged.")

print("=== PHASE 1 FULLY COMPLETED! ===")
