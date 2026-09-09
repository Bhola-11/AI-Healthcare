from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from .models import AuditLog
from .services import AuditService
import csv

def is_compliance_officer(user):
    return user.is_authenticated and (user.is_superuser or user.role in ['ADMIN', 'COMPLIANCE'])

@login_required
@user_passes_test(is_compliance_officer)
def audit_search_view(request):
    query = request.GET.get('q', '')
    action = request.GET.get('action', '')
    logs = AuditLog.objects.select_related('actor').all()
    
    if query:
        logs = logs.filter(resource_type__icontains=query)
    if action:
        logs = logs.filter(action=action)
        
    logs = logs[:100]
    tamper_status = AuditService.verify_chain_integrity()
    
    return render(request, 'audit/search.html', {
        'logs': logs,
        'tamper_status': tamper_status,
        'query': query,
        'action': action,
        'action_choices': AuditLog.Action.choices
    })

@login_required
@user_passes_test(is_compliance_officer)
def audit_export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="hipaa_audit_trail_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Timestamp', 'Actor', 'Action', 'Resource Type', 'Resource ID', 'Status', 'Tamper Hash'])
    
    for log in AuditLog.objects.select_related('actor').all()[:1000]:
        writer.writerow([
            str(log.id),
            log.created_at.isoformat(),
            log.actor.email if log.actor else 'SYSTEM',
            log.action,
            log.resource_type,
            log.resource_id,
            log.status,
            log.tamper_evident_hash
        ])
    return response
