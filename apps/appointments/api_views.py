from rest_framework import viewsets, permissions
from .models import Appointment, QueueTicket
from .serializers import AppointmentSerializer, QueueTicketSerializer

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.select_related('patient__user', 'doctor__user', 'facility').all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'doctor', 'facility', 'consultation_type']

class QueueTicketViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = QueueTicket.objects.select_related('appointment').all()
    serializer_class = QueueTicketSerializer
    permission_classes = [permissions.IsAuthenticated]
