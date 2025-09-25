# payment/views.py
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import PaymentMethod, PaymentConfirmation
from .serializers import PaymentMethodSerializer, PaymentConfirmationSerializer
from orders.models import Order
import logging

logger = logging.getLogger(__name__)

class PaymentMethodListView(generics.ListAPIView):
    """List available payment methods"""
    queryset = PaymentMethod.objects.filter(is_active=True)
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.AllowAny]

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_payment_confirmation(request, order_id):
    """Submit transaction ID and payment screenshot for an order"""
    try:
        order = get_object_or_404(Order, order_id=order_id, user=request.user)
        payment_confirmation, created = PaymentConfirmation.objects.get_or_create(order=order)
        
        # Update fields
        serializer = PaymentConfirmationSerializer(
            payment_confirmation,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Payment confirmation submitted for order {order_id} by user {request.user.email}")
            return Response({
                'message': 'Payment confirmation submitted successfully',
                'payment_confirmation': serializer.data
            }, status=status.HTTP_200_OK)
        logger.error(f"Invalid submission data for order {order_id}: {serializer.errors}")
        return Response({
            'error': 'Invalid submission data',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found or not owned by user {request.user.email}")
        return Response(
            {'error': 'Order not found or you do not have permission'},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['PATCH'])
@permission_classes([permissions.IsAdminUser])
def review_payment_confirmation(request, order_id):
    """Admin reviews and updates payment confirmation and order status"""
    try:
        order = get_object_or_404(Order, order_id=order_id)
        payment_confirmation = get_object_or_404(PaymentConfirmation, order=order)
        data = request.data
        status = data.get('status')
        confirmation_notes = data.get('confirmation_notes')

        if status not in ['approved', 'rejected']:
            return Response(
                {'error': 'Status must be "approved" or "rejected"'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update order status
        order.status = status
        order.save()

        # Update payment confirmation
        payment_confirmation.confirmed_by = request.user
        payment_confirmation.confirmation_notes = confirmation_notes or payment_confirmation.confirmation_notes
        payment_confirmation.updated_at = timezone.now()
        payment_confirmation.save()

        logger.info(f"Payment confirmation for order {order_id} {status} by admin {request.user.email}")
        return Response({
            'message': f'Payment confirmation {status} successfully',
            'payment_confirmation': PaymentConfirmationSerializer(payment_confirmation, context={'request': request}).data
        }, status=status.HTTP_200_OK)
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found")
        return Response(
            {'error': 'Order not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except PaymentConfirmation.DoesNotExist:
        logger.error(f"Payment confirmation for order {order_id} not found")
        return Response(
            {'error': 'Payment confirmation not found'},
            status=status.HTTP_404_NOT_FOUND
        )