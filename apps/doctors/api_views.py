from rest_framework import viewsets, permissions
from .models import DoctorProfile, Specialty, DoctorSchedule
from .serializers import DoctorSerializer, SpecialtySerializer, DoctorScheduleSerializer

class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DoctorProfile.objects.filter(user__is_active=True)
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]

class SpecialtyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Specialty.objects.all()
    serializer_class = SpecialtySerializer
    permission_classes = [permissions.IsAuthenticated]

class DoctorScheduleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DoctorSchedule.objects.filter(is_active=True)
    serializer_class = DoctorScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
