from rest_framework import viewsets, permissions
from .models import Facility, Department, Ward, Room, Bed
from .serializers import FacilitySerializer, DepartmentSerializer, WardSerializer, RoomSerializer, BedSerializer

class FacilityViewSet(viewsets.ModelViewSet):
    queryset = Facility.objects.filter(is_active=True)
    serializer_class = FacilitySerializer
    permission_classes = [permissions.IsAuthenticated]

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.filter(is_active=True)
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]

class BedViewSet(viewsets.ModelViewSet):
    queryset = Bed.objects.all()
    serializer_class = BedSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'room__ward__department__facility']
