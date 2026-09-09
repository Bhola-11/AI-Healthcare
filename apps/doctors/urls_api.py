from rest_framework.routers import DefaultRouter
from .api_views import DoctorViewSet, SpecialtyViewSet, DoctorScheduleViewSet

router = DefaultRouter()
router.register(r'doctors', DoctorViewSet, basename='api-doctor')
router.register(r'specialties', SpecialtyViewSet, basename='api-specialty')
router.register(r'schedules', DoctorScheduleViewSet, basename='api-schedule')

urlpatterns = router.urls
