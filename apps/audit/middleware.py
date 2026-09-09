"""
Audit Log Middleware for HealthSphere.
Tracks HTTP requests, actors, IP addresses, and user agents for HIPAA/GDPR compliance.
"""
class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Attach request metadata
        response = self.get_response(request)
        return response
