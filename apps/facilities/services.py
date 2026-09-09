from .models import Bed, Facility

class BedOccupancyService:
    @staticmethod
    def calculate_facility_occupancy(facility_id):
        beds = Bed.objects.filter(room__ward__department__facility_id=facility_id)
        total = beds.count()
        if total == 0:
            return {"total": 0, "occupied": 0, "available": 0, "rate": 0.0}
        occupied = beds.filter(status=Bed.Status.OCCUPIED).count()
        available = beds.filter(status=Bed.Status.AVAILABLE).count()
        rate = round((occupied / total) * 100, 2)
        return {
            "total": total,
            "occupied": occupied,
            "available": available,
            "rate": rate
        }

    @staticmethod
    def find_available_bed(facility_id, ward_type=None):
        qs = Bed.objects.filter(
            room__ward__department__facility_id=facility_id,
            status=Bed.Status.AVAILABLE
        )
        if ward_type:
            qs = qs.filter(room__ward__ward_type=ward_type)
        return qs.first()
