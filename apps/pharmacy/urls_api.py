from rest_framework.routers import DefaultRouter
from .api_views import MedicationViewSet, PrescriptionViewSet

router = DefaultRouter()
router.register(r'medications', MedicationViewSet, basename='api-medication')
router.register(r'prescriptions', PrescriptionViewSet, basename='api-prescription')

urlpatterns = router.urls
