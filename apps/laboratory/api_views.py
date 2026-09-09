from rest_framework import viewsets, permissions
from .models import LabTestCatalog, LabOrder, LabResultItem
from .serializers import LabTestCatalogSerializer, LabOrderSerializer, LabResultItemSerializer

class LabCatalogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LabTestCatalog.objects.filter(is_active=True)
    serializer_class = LabTestCatalogSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['test_name', 'loinc_code', 'category']

class LabOrderViewSet(viewsets.ModelViewSet):
    queryset = LabOrder.objects.select_related('patient__user', 'ordering_doctor__user').prefetch_related('results').all()
    serializer_class = LabOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'priority', 'patient', 'ordering_doctor']
