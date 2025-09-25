from django.db import models
from django.utils import timezone
import uuid
import qrcode
from io import BytesIO
from django.core.files import File
from orders.models import Order


class Ticket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_id = models.CharField(max_length=20, unique=True, null=True, blank=True)  # Add null=True, blank=True
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tickets')
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            timestamp = str(int(timezone.now().timestamp()))
            self.ticket_id = f"TKT{timestamp}{self.order.id.hex[:6]}"

        super().save(*args, **kwargs)

        if not self.qr_code:
            self.generate_qr_code()

    def generate_qr_code(self):
        qr_data = {
            'ticket_id': self.ticket_id,
            'event_id': str(self.order.event.id),
            'user_id': str(self.order.user.id),
            'order_id': self.order.order_id
        }

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(str(qr_data))
        qr.make(fit=True)

        qr_image = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        buffer.seek(0)

        filename = f'qr_{self.ticket_id}.png'
        self.qr_code.save(filename, File(buffer), save=True)

    def mark_as_used(self):
        self.is_used = True
        self.used_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.ticket_id} - {self.order.event.title}"







