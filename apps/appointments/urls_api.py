from rest_framework.routers import DefaultRouter
from .api_views import AppointmentViewSet, QueueTicketViewSet

router = DefaultRouter()
router.register(r'appointments', AppointmentViewSet, basename='api-appointment')
router.register(r'queue-tickets', QueueTicketViewSet, basename='api-queue-ticket')

urlpatterns = router.urls
