from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import InsuranceClaim, InsuranceProvider, PatientInsurancePolicy

@login_required
def claim_list(request):
    claims = InsuranceClaim.objects.select_related('policy__patient__user', 'policy__provider').all()[:50]
    return render(request, 'insurance/claim_list.html', {'claims': claims})
