from rest_framework import serializers
from .models import Appointment, QueueTicket

class QueueTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueueTicket
        fields = '__all__'

class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)
    facility_name = serializers.CharField(source='facility.name', read_only=True)
    queue_ticket = QueueTicketSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'
