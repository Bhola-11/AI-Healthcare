from rest_framework import viewsets, permissions
from .models import Invoice, FeeSchedule, Payment
from .serializers import InvoiceSerializer, FeeScheduleSerializer, PaymentSerializer

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related('patient__user').prefetch_related('items', 'payments').all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'patient']

class FeeScheduleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FeeSchedule.objects.filter(is_active=True)
    serializer_class = FeeScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['code', 'description', 'category']
