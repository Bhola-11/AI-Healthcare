from rest_framework import serializers
from .models import Medication, BatchInventory, DispensationRecord
from apps.prescriptions.models import Prescription, PrescriptionItem

class PrescriptionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionItem
        fields = '__all__'

class PrescriptionSerializer(serializers.ModelSerializer):
    items = PrescriptionItemSerializer(many=True, read_only=True)
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)

    class Meta:
        model = Prescription
        fields = '__all__'

class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchInventory
        fields = '__all__'

class MedicationSerializer(serializers.ModelSerializer):
    batches = BatchSerializer(many=True, read_only=True)
    class Meta:
        model = Medication
        fields = '__all__'
