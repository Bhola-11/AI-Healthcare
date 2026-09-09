import re
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
