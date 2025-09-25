from django.db import models
from django.utils import timezone
import uuid

# Avoid importing Ticket or Order directly here — use string references instead
from users.models import User
from events.models import Event


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_id = models.CharField(max_length=20, unique=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='orders')
    quantity = models.PositiveIntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=[
    ('credit_card', 'Credit Card'),
    ('bank_transfer', 'Bank Transfer'),
    ('mobile_money', 'Mobile Money'), ])
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    payment_confirmed_at = models.DateTimeField(blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_id:
            timestamp = str(int(timezone.now().timestamp()))
            self.order_id = f"ORD{timestamp}"

        self.total_amount = self.event.price * self.quantity

        if self.status == 'approved' and not self.payment_confirmed_at:
            self.payment_confirmed_at = timezone.now()

        super().save(*args, **kwargs)

        if self.status == 'approved':
            self.create_tickets()

    def create_tickets(self):
        """Create tickets for approved orders"""
        if self.tickets.exists():
            return

        Ticket = self._get_ticket_model()
        for _ in range(self.quantity):
            Ticket.objects.create(order=self)

    def _get_ticket_model(self):
        """Lazy import Ticket to avoid circular import"""
        from tickets.models import Ticket
        return Ticket

    def __str__(self):
        return f"{self.order_id} - {self.user.get_full_name()} - {self.event.title}"


