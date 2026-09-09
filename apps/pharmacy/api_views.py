from rest_framework import viewsets, permissions
from .models import Medication, BatchInventory
from apps.prescriptions.models import Prescription
from .serializers import MedicationSerializer, BatchSerializer, PrescriptionSerializer

class MedicationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Medication.objects.filter(is_active=True).prefetch_related('batches')
    serializer_class = MedicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['brand_name', 'generic_name', 'atc_code']

class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.select_related('patient__user', 'doctor__user').prefetch_related('items').all()
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'doctor', 'patient']
