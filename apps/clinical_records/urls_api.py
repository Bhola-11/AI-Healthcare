from rest_framework.routers import DefaultRouter
from .api_views import EncounterViewSet, ICD10ViewSet

router = DefaultRouter()
router.register(r'encounters', EncounterViewSet, basename='api-encounter')
router.register(r'icd10', ICD10ViewSet, basename='api-icd10')

urlpatterns = router.urls
