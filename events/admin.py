# events/admin.py
from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'price', 'location', 'organizer', 'created_at')
    list_filter = ('date', 'location', 'organizer')
    search_fields = ('title', 'description', 'location', 'organizer__username')
    prepopulated_fields = {'title': ('title',)}
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')