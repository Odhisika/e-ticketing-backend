from rest_framework import serializers
from .models import Order
from events.serializers import EventSerializer
from tickets.serializers import TicketSerializer
from users.serializers import UserSerializer
from events.models import Event
from users.models import User
from payment.serializers import PaymentConfirmationSerializer
from payment.models import PaymentMethod

class OrderCreateSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    event_id = serializers.IntegerField() 
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=True, read_only=True)
    tickets = TicketSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'user', 'event', 'event_id', 'quantity',
            'total_amount', 'payment_method', 'status', 'payment_reference',
            'admin_notes', 'created_at', 'updated_at', 'tickets'
        ]
        read_only_fields = ['order_id', 'total_amount', 'user']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user:
            validated_data['user'] = request.user
        return super().create(validated_data)

    def validate_event_id(self, value):
        try:
            event = Event.objects.get(id=value, is_active=True)
            return value
        except Event.DoesNotExist:
            raise serializers.ValidationError("Event not found or inactive")

    def validate_quantity(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError("Quantity must be between 1 and 10")
        return value

class OrderSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    event_id = serializers.IntegerField(write_only=True)   # 👈 change UUIDField → IntegerField
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=True, read_only=True)
    tickets = TicketSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'user', 'event', 'event_id', 'quantity',
            'total_amount', 'payment_method', 'status', 'payment_reference',
            'admin_notes', 'created_at', 'updated_at', 'tickets'
        ]
        read_only_fields = ['order_id', 'total_amount', 'user']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user:
            validated_data['user'] = request.user
        return super().create(validated_data)

    def validate_event_id(self, value):
        try:
            event = Event.objects.get(id=value, is_active=True)
            return value
        except Event.DoesNotExist:
            raise serializers.ValidationError("Event not found or inactive")



class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    admin_notes = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Order
        fields = ['status', 'admin_notes']

    def validate_status(self, value):
        if value not in ['pending', 'approved', 'rejected']:
            raise serializers.ValidationError("Invalid status")
        return value

class AdminOrderListSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=True)
    tickets_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'user', 'event', 'quantity', 'total_amount',
            'payment_method', 'status', 'payment_reference', 'tickets_count',
            'created_at', 'updated_at'
        ]

    def get_tickets_count(self, obj):
        return obj.tickets.count()

class AdminOrderDetailSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    tickets = TicketSerializer(many=True, read_only=True)
    payment_confirmation = PaymentConfirmationSerializer(read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'user', 'event', 'quantity', 'total_amount',
            'payment_method', 'status', 'payment_reference', 'admin_notes',
            'payment_confirmed_at', 'created_at', 'updated_at', 'tickets',
            'payment_confirmation'
        ]