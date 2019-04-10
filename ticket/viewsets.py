from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from gatheros_event.models import Event
from ticket.models import Ticket, Lot
from ticket.serializers import TicketSerializer, LotSerializer
from .permissions import OrganizerOnly


class TicketRestrictionMixin:
    permission_classes = (IsAuthenticated, OrganizerOnly)
    authentication_classes = (
        SessionAuthentication,
        BasicAuthentication,
        TokenAuthentication,
    )


class TicketViewSet(TicketRestrictionMixin, viewsets.ModelViewSet):
    serializer_class = TicketSerializer

    def get_queryset(self) -> QuerySet:
        qs = Event.objects.filter(
            organization__members__person__user=self.request.user
        )

        return Ticket.objects.filter(
            event_id__in=[str(event.pk) for event in qs]
        )


class LotViewSet(TicketRestrictionMixin, viewsets.ModelViewSet):
    serializer_class = LotSerializer
    queryset = Lot.objects.all()
