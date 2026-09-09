from datetime import timedelta
from django.utils import timezone
from .models import BatchInventory

class PharmacyAlertService:
    @staticmethod
    def get_expiring_batches(days=30):
        cutoff = timezone.now().date() + timedelta(days=days)
        return BatchInventory.objects.filter(expiry_date__lte=cutoff, quantity_on_hand__gt=0).select_related('medication')

    @staticmethod
    def get_low_stock_items():
        return BatchInventory.objects.filter(quantity_on_hand__lte=models.F('reorder_level')).select_related('medication')
