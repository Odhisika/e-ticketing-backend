# tickets/serializers.py
from rest_framework import serializers
from .models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    qr_code = serializers.SerializerMethodField()
    order = serializers.SerializerMethodField()  # Add order data

    class Meta:
        model = Ticket
        fields = ['id', 'ticket_id', 'qr_code', 'is_used', 'created_at', 'order']

    def get_qr_code(self, obj):
        if obj.qr_code:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.qr_code.url)
            return obj.qr_code.url
        return None

    def get_order(self, obj):
        # Return minimal order data
        return {
            'id': str(obj.order.id),  # UUID as string
            'status': obj.order.status,
            'event': {
                'id': str(obj.order.event.id),
                'title': obj.order.event.title,
                'date': obj.order.event.date.isoformat(),
                'location': obj.order.event.location,
            },
            'quantity': obj.order.quantity,
        }
    

class TicketValidationSerializer(serializers.Serializer):
    """Serializer for ticket validation"""
    ticket_id = serializers.CharField(max_length=20)

    def validate_ticket_id(self, value):
        try:
            ticket = Ticket.objects.get(ticket_id=value)
            if ticket.is_used:
                raise serializers.ValidationError("Ticket has already been used")
            if ticket.order.status != 'approved':
                raise serializers.ValidationError("Order not approved")
            return value
        except Ticket.DoesNotExist:
            raise serializers.ValidationError("Invalid ticket ID")