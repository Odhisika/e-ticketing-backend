# payment/serializers.py
from rest_framework import serializers
from .models import PaymentMethod, PaymentConfirmation
from users.serializers import UserSerializer


class PaymentMethodSerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()

    class Meta:
        model = PaymentMethod
        fields = ['id', 'type', 'name', 'details']

    def get_details(self, obj):
        if obj.type == 'bank':
            return {
                'account_name': obj.account_name,
                'account_number': obj.account_number,
                'bank_name': obj.bank_name,
                'branch': obj.branch,
                'sort_code': obj.sort_code,
            }
        elif obj.type == 'mobile_money':
            return {
                'number': obj.momo_number,
                'name': obj.account_name,
                'network': obj.network,
            }
        return {}

class PaymentConfirmationSerializer(serializers.ModelSerializer):
    order = serializers.SerializerMethodField()
    confirmed_by = UserSerializer(read_only=True)

    class Meta:
        model = PaymentConfirmation
        fields = [
            'id', 'order', 'confirmed_by', 'transaction_id', 'payment_screenshot',
            'confirmation_notes', 'created_at', 'updated_at'
        ]

    def get_order(self, obj):
        from orders.serializers import OrderSerializer
        return OrderSerializer(obj.order, context=self.context).data