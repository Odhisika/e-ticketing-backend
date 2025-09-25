from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'event', 'quantity', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'event')
    search_fields = ('order_id', 'user__username', 'event__title')
    readonly_fields = ('order_id', 'created_at', 'updated_at')
    actions = ['approve_orders', 'reject_orders']

    def approve_orders(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, f"{queryset.count()} orders were successfully approved.")
    approve_orders.short_description = "Approve selected orders"

    def reject_orders(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f"{queryset.count()} orders were successfully rejected.")
    reject_orders.short_description = "Reject selected orders"

    