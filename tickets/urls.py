from django.urls import path
from tickets.views import TicketListView, TicketDetailView, validate_ticket

urlpatterns = [
    path("tickets/", TicketListView.as_view(), name="ticket-list"),
    path("tickets/<uuid:pk>/", TicketDetailView.as_view(), name="ticket-detail"),
    path("tickets/validate/", validate_ticket, name="ticket-validate"),
]
