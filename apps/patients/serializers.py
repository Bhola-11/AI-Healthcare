from rest_framework import serializers
from .models import PatientProfile, VitalSign, Allergy, EmergencyContact

class VitalSignSerializer(serializers.ModelSerializer):
    map_score = serializers.FloatField(source='calculate_mean_arterial_pressure', read_only=True)
    class Meta:
        model = VitalSign
        fields = '__all__'

class AllergySerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergy
        fields = '__all__'

class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = '__all__'

class PatientSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    vital_signs = VitalSignSerializer(many=True, read_only=True)
    allergies = AllergySerializer(many=True, read_only=True)
    emergency_contacts = EmergencyContactSerializer(many=True, read_only=True)

    class Meta:
        model = PatientProfile
        fields = '__all__'
