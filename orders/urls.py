from django.urls import path
from . import views

urlpatterns = [
    # Order-related endpoints
    path('orders/', views.OrderCreateView.as_view(), name='order-create'),
    path('orders/list/', views.OrderListView.as_view(), name='order-list'),
    path('orders/<uuid:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('orders/<uuid:pk>/status/', views.OrderStatusUpdateView.as_view(), name='order-status-update'),
    path('orders/<uuid:order_id>/approve/', views.approve_order, name='order-approve'),
    path('orders/<uuid:order_id>/reject/', views.reject_order, name='order-reject'),
    path('orders/<str:order_id>/status/', views.OrderStatusView.as_view(), name='order-status'),
    path('orders/<str:order_id>/payment-status/', views.check_payment_status, name='check-payment-status'),


    # Admin-specific endpoints
    path('admin/orders/', views.AdminPendingOrdersView.as_view(), name='admin-pending-orders'),

    # Payment method endpoint
    path('payment-methods/', views.PaymentMethodListView.as_view(), name='payment-method-list'),
    path('orders/debug-order-data/', views.DebugOrderDataView.as_view(), name='debug-order-data'),
]