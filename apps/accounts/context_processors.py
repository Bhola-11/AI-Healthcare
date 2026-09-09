"""
User roles context processor for templates.
"""
def user_roles(request):
    if hasattr(request, 'user') and request.user.is_authenticated:
        return {
            'current_user_role': getattr(request.user, 'role', 'GUEST'),
            'is_doctor': getattr(request.user, 'role', '') == 'DOCTOR',
            'is_patient': getattr(request.user, 'role', '') == 'PATIENT',
            'is_nurse': getattr(request.user, 'role', '') == 'NURSE',
            'is_pharmacist': getattr(request.user, 'role', '') == 'PHARMACIST',
            'is_lab_tech': getattr(request.user, 'role', '') == 'LAB_TECH',
            'is_biller': getattr(request.user, 'role', '') == 'BILLER',
            'is_admin': getattr(request.user, 'role', '') == 'ADMIN' or request.user.is_superuser,
        }
    return {
        'current_user_role': 'GUEST',
        'is_doctor': False,
        'is_patient': False,
        'is_nurse': False,
        'is_pharmacist': False,
        'is_lab_tech': False,
        'is_biller': False,
        'is_admin': False,
    }
