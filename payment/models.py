# payment/models.py
from django.db import models
import uuid
from users.models import User

class PaymentMethod(models.Model):
    PAYMENT_TYPES = [
        ('bank', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=100, choices=PAYMENT_TYPES)
    name = models.CharField(max_length=100)
    account_name = models.CharField(max_length=200, blank=True, null=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    branch = models.CharField(max_length=100, blank=True, null=True)
    sort_code = models.CharField(max_length=20, blank=True, null=True)
    momo_number = models.CharField(max_length=15, blank=True, null=True)
    network = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_type_display()} - {self.name}"

class PaymentConfirmation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='payment_confirmation')
    confirmed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    transaction_id = models.CharField(max_length=50, blank=True, null=True)  # New field
    payment_screenshot = models.ImageField(upload_to='payment_confirmations/', blank=True, null=True)
    confirmation_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment confirmation for {self.order.order_id}"