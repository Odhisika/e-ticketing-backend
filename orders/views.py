from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q

import logging

from orders.models import Order
from payment.models import PaymentMethod
from events.models import Event
from users.models import User
from tickets.models import Ticket
from .serializers import (
    EventSerializer, OrderSerializer, OrderCreateSerializer,
    OrderStatusUpdateSerializer, AdminOrderListSerializer, AdminOrderDetailSerializer
)
from payment.serializers import PaymentMethodSerializer  # Import PaymentMethodSerializer from payment.serializers


logger = logging.getLogger(__name__)

class OrderCreateView(generics.CreateAPIView):
    """Create a new order"""
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Debug logging
        logger.info("=== ORDER CREATE REQUEST ===")
        logger.info(f"User: {request.user}")
        logger.info(f"User ID: {request.user.id}")
        logger.info(f"Is authenticated: {request.user.is_authenticated}")
        logger.info(f"Request data: {request.data}")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Content type: {request.content_type}")
        
        # Validate request data
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response({
                'error': 'Invalid data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Create order
            order = serializer.save(user=request.user)
            logger.info(f"Order created successfully: {order.order_id}")
            
            # Return full order details
            response_serializer = OrderSerializer(order, context={'request': request})
            
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            return Response({
                'error': 'Failed to create order',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

# Also add a simple debug view to check what data is being received
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def debug_order_data(request):
    """Debug view to check order creation data"""
    logger.info("=== DEBUG ORDER DATA ===")
    logger.info(f"User: {request.user}")
    logger.info(f"Request data: {request.data}")
    logger.info(f"Request data type: {type(request.data)}")
    
    # Check each field
    event_id = request.data.get('event_id')
    quantity = request.data.get('quantity')
    payment_method = request.data.get('payment_method')
    
    logger.info(f"event_id: {event_id} (type: {type(event_id)})")
    logger.info(f"quantity: {quantity} (type: {type(quantity)})")
    logger.info(f"payment_method: {payment_method} (type: {type(payment_method)})")
    
    # Check if event exists
    if event_id:
        from events.models import Event
        try:
            event = Event.objects.get(id=event_id, is_active=True)
            logger.info(f"Event found: {event.title}")
        except Event.DoesNotExist:
            logger.error(f"Event not found with id: {event_id}")
        except Exception as e:
            logger.error(f"Error finding event: {e}")
    
    return Response({
        'message': 'Debug data received',
        'user': str(request.user),
        'data': request.data,
        'event_id': event_id,
        'quantity': quantity,
        'payment_method': payment_method,
    })


class OrderListView(generics.ListAPIView):
    """List user's orders"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
   

class OrderDetailView(generics.RetrieveAPIView):
    """Get order details"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class OrderStatusUpdateView(generics.UpdateAPIView):
    """Update order status (for admins or payment confirmation)"""
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_admin:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Only admins can change status to approved/rejected
        if 'status' in request.data and request.data['status'] in ['approved', 'rejected']:
            if not request.user.is_admin:
                return Response(
                    {'error': 'Only admins can approve or reject orders'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Return full order details
        response_serializer = OrderSerializer(instance, context={'request': request})
        return Response(response_serializer.data)

# Admin Views
class AdminPendingOrdersView(generics.ListAPIView):
    """List pending orders for admin"""
    serializer_class = AdminOrderListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_admin:
            return Order.objects.none()
        
        status_filter = self.request.query_params.get('status', 'pending')
        return Order.objects.filter(status=status_filter)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def approve_order(request, order_id):
    """Approve an order (admin only)"""
    if not request.user.is_admin:
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    order = get_object_or_404(Order, id=order_id)
    
    if order.status != 'pending':
        return Response(
            {'error': f'Order is already {order.status}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update order status
    order.status = 'approved'
    order.admin_notes = request.data.get('notes', '')
    order.save()
    
    # Return updated order
    serializer = AdminOrderDetailSerializer(order, context={'request': request})
    return Response({
        'message': 'Order approved successfully',
        'order': serializer.data
    })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reject_order(request, order_id):
    """Reject an order (admin only)"""
    if not request.user.is_admin:
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    order = get_object_or_404(Order, id=order_id)
    
    if order.status != 'pending':
        return Response(
            {'error': f'Order is already {order.status}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update order status
    order.status = 'rejected'
    order.admin_notes = request.data.get('notes', 'Order rejected by admin')
    order.save()
    
    # Return updated order
    serializer = AdminOrderDetailSerializer(order, context={'request': request})
    return Response({
        'message': 'Order rejected successfully',
        'order': serializer.data
    })

# Additional utility views
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_payment_status(request, order_id):
    """Check payment status for an order"""
    try:
        if request.user.is_admin:
            order = Order.objects.get(order_id=order_id)
        else:
            order = Order.objects.get(order_id=order_id, user=request.user)
        
        serializer = OrderSerializer(order, context={'request': request})
        return Response({
            'order': serializer.data,
            'status': order.status,
            'message': {
                'pending': 'Payment is being processed',
                'approved': 'Payment confirmed and tickets generated',
                'rejected': 'Payment was rejected'
            }.get(order.status, 'Unknown status')
        })
        
    except Order.DoesNotExist:
        return Response(
            {'error': 'Order not found'},
            status=status.HTTP_404_NOT_FOUND
        )

class OrderStatusView(APIView):
    """Get order status by order ID"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, order_id):
        try:
            if request.user.is_admin:
                order = Order.objects.get(order_id=order_id)
            else:
                order = Order.objects.get(order_id=order_id, user=request.user)
            
            return Response({
                'order_id': order.order_id,
                'status': order.status,
                'total_amount': str(order.total_amount),
                'created_at': order.created_at,
                'payment_method': order.payment_method,
                'event_title': order.event.title,
            })
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class PaymentMethodListView(generics.ListAPIView):
    """List available payment methods"""
    queryset = PaymentMethod.objects.filter(is_active=True)
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.AllowAny]


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class DebugOrderDataView(APIView):
    def post(self, request):
        # Add your debugging logic here
        data = request.data
        return Response({"message": "Debug data received", "data": data}, status=status.HTTP_200_OK)