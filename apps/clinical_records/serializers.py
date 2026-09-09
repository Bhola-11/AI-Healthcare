from rest_framework import serializers
from .models import Encounter, SOAPNote, EncounterDiagnosis, ICD10DiagnosisCode

class ICD10Serializer(serializers.ModelSerializer):
    class Meta:
        model = ICD10DiagnosisCode
        fields = '__all__'

class SOAPNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SOAPNote
        fields = '__all__'

class EncounterDiagnosisSerializer(serializers.ModelSerializer):
    icd10_detail = ICD10Serializer(source='icd10', read_only=True)
    class Meta:
        model = EncounterDiagnosis
        fields = '__all__'

class EncounterSerializer(serializers.ModelSerializer):
    soap_note = SOAPNoteSerializer(read_only=True)
    diagnoses = EncounterDiagnosisSerializer(many=True, read_only=True)
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)

    class Meta:
        model = Encounter
        fields = '__all__'
