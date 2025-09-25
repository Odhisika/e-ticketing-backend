from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from tickets.models import Ticket
from django.utils import timezone
from tickets.serializers import TicketSerializer, TicketValidationSerializer



class TicketListView(generics.ListAPIView):
    """List tickets for the authenticated user"""
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Ticket.objects.filter(order__user=self.request.user)

class TicketDetailView(generics.RetrieveAPIView):
    """Get ticket details"""
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Ticket.objects.filter(order__user=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def validate_ticket(request):
    """Validate a ticket by ticket_id"""
    serializer = TicketValidationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    ticket_id = serializer.validated_data['ticket_id']
    try:
        ticket = Ticket.objects.get(ticket_id=ticket_id)
        if ticket.is_used:
            return Response(
                {'error': 'Ticket has already been used'},
                status=status.HTTP_400_BAD_REQUEST
            )
        ticket.is_used = True
        ticket.used_at = timezone.now()
        ticket.save()
        return Response({
            'message': 'Ticket validated successfully',
            'ticket': TicketSerializer(ticket, context={'request': request}).data
        })
    except Ticket.DoesNotExist:
        return Response(
            {'error': 'Ticket not found'},
            status=status.HTTP_404_NOT_FOUND
        )