from rest_framework import serializers
from .models import Invoice, InvoiceItem, Payment, FeeSchedule

class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)

    class Meta:
        model = Invoice
        fields = '__all__'

class FeeScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeSchedule
        fields = '__all__'
