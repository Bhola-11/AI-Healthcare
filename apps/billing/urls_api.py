from rest_framework.routers import DefaultRouter
from .api_views import InvoiceViewSet, FeeScheduleViewSet

router = DefaultRouter()
router.register(r'invoices', InvoiceViewSet, basename='api-invoice')
router.register(r'fee-schedules', FeeScheduleViewSet, basename='api-fee-schedule')

urlpatterns = router.urls
