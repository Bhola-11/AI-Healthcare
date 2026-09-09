"""
Root URL Configuration for HealthSphere.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='accounts:login', permanent=False), name='home'),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('facilities/', include('apps.facilities.urls', namespace='facilities')),
    path('doctors/', include('apps.doctors.urls', namespace='doctors')),
    path('patients/', include('apps.patients.urls', namespace='patients')),
    path('appointments/', include('apps.appointments.urls', namespace='appointments')),
    path('clinical/', include('apps.clinical_records.urls', namespace='clinical_records')),
    path('prescriptions/', include('apps.prescriptions.urls', namespace='prescriptions')),
    path('pharmacy/', include('apps.pharmacy.urls', namespace='pharmacy')),
    path('laboratory/', include('apps.laboratory.urls', namespace='laboratory')),
    path('billing/', include('apps.billing.urls', namespace='billing')),
    path('insurance/', include('apps.insurance.urls', namespace='insurance')),
    path('notifications/', include('apps.notifications.urls', namespace='notifications')),
    path('analytics/', include('apps.analytics.urls', namespace='analytics')),
    path('ai/', include('apps.ai_engine.urls', namespace='ai_engine')),
    path('audit/', include('apps.audit.urls', namespace='audit')),
    path('api/', include('apps.api.urls', namespace='api')),
    
    # OpenAPI Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
