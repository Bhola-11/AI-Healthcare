from rest_framework.routers import DefaultRouter
from .api_views import PatientViewSet, VitalSignViewSet, AllergyViewSet

router = DefaultRouter()
router.register(r'patients', PatientViewSet, basename='api-patient')
router.register(r'vitals', VitalSignViewSet, basename='api-vitals')
router.register(r'allergies', AllergyViewSet, basename='api-allergies')

urlpatterns = router.urls
