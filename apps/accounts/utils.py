import secrets
import string

def generate_medical_record_number(prefix="MRN"):
    chars = string.ascii_uppercase + string.digits
    rand = ''.join(secrets.choice(chars) for _ in range(8))
    return f"{prefix}-{rand}"

def sanitize_phi_text(text):
    if not text:
        return ""
    return " ".join(text.strip().split())
