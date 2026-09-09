from rest_framework.routers import DefaultRouter
from .api_views import LabCatalogViewSet, LabOrderViewSet

router = DefaultRouter()
router.register(r'catalog', LabCatalogViewSet, basename='api-lab-catalog')
router.register(r'orders', LabOrderViewSet, basename='api-lab-order')

urlpatterns = router.urls
