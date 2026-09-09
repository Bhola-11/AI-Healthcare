from rest_framework import viewsets, permissions
from .models import Encounter, SOAPNote, EncounterDiagnosis, ICD10DiagnosisCode
from .serializers import EncounterSerializer, SOAPNoteSerializer, EncounterDiagnosisSerializer, ICD10Serializer

class EncounterViewSet(viewsets.ModelViewSet):
    queryset = Encounter.objects.select_related('patient__user', 'doctor__user', 'facility', 'soap_note').all()
    serializer_class = EncounterSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['patient', 'doctor', 'status', 'encounter_class']

class ICD10ViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ICD10DiagnosisCode.objects.all()
    serializer_class = ICD10Serializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['code', 'description']
