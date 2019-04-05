from rest_framework import viewsets

from ticket.models import Ticket, Lot
from ticket.serializers import TicketSerializer, LotSerializer


class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    queryset = Ticket.objects.all()


class LotViewSet(viewsets.ModelViewSet):
    serializer_class = LotSerializer
    queryset = Lot.objects.all()
