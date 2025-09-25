from django.contrib import admin
from .models import Ticket

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_id', 'order', 'created_at', 'is_used']
    list_filter = ['created_at', 'is_used']
    readonly_fields = ['created_at']