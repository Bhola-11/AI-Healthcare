def mask_ssn(ssn):
    if not ssn or len(ssn) < 4:
        return "****"
    return f"***-**-{ssn[-4:]}"

def mask_email(email):
    if not email or '@' not in email:
        return "***"
    user, domain = email.split('@', 1)
    masked_user = user[0] + '***' + (user[-1] if len(user) > 1 else '')
    return f"{masked_user}@{domain}"
