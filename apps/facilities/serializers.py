from rest_framework import serializers
from .models import Facility, Department, Ward, Room, Bed

class BedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bed
        fields = '__all__'

class RoomSerializer(serializers.ModelSerializer):
    beds = BedSerializer(many=True, read_only=True)
    class Meta:
        model = Room
        fields = '__all__'

class WardSerializer(serializers.ModelSerializer):
    rooms = RoomSerializer(many=True, read_only=True)
    class Meta:
        model = Ward
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    wards = WardSerializer(many=True, read_only=True)
    class Meta:
        model = Department
        fields = '__all__'

class FacilitySerializer(serializers.ModelSerializer):
    departments = DepartmentSerializer(many=True, read_only=True)
    class Meta:
        model = Facility
        fields = '__all__'
