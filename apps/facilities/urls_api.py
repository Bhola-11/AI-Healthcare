from rest_framework.routers import DefaultRouter
from .api_views import FacilityViewSet, DepartmentViewSet, BedViewSet

router = DefaultRouter()
router.register(r'facilities', FacilityViewSet, basename='api-facility')
router.register(r'departments', DepartmentViewSet, basename='api-department')
router.register(r'beds', BedViewSet, basename='api-bed')

urlpatterns = router.urls
