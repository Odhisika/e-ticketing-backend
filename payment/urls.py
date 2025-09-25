# payment/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('payment-methods/', views.PaymentMethodListView.as_view(), name='payment-method-list'),
    path('payments/<str:order_id>/submit-confirmation/', views.submit_payment_confirmation, name='submit-payment-confirmation'),
    path('payments/<str:order_id>/review-confirmation/', views.review_payment_confirmation, name='review-payment-confirmation'),
]