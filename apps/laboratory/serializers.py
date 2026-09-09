from rest_framework import serializers
from .models import LabTestCatalog, SpecimenType, LabOrder, LabSpecimen, LabResultItem

class LabTestCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabTestCatalog
        fields = '__all__'

class LabResultItemSerializer(serializers.ModelSerializer):
    test_name = serializers.CharField(source='test.test_name', read_only=True)
    measurement_unit = serializers.CharField(source='test.measurement_unit', read_only=True)
    class Meta:
        model = LabResultItem
        fields = '__all__'

class LabOrderSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)
    doctor_name = serializers.CharField(source='ordering_doctor.user.get_full_name', read_only=True)
    results = LabResultItemSerializer(many=True, read_only=True)

    class Meta:
        model = LabOrder
        fields = '__all__'
