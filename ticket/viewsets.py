from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ticket.models import Ticket, Lot
from ticket.serializers import TicketSerializer, LotSerializer


class TicketViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TicketSerializer
    queryset = Ticket.objects.all()


class LotViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = LotSerializer
    queryset = Lot.objects.all()
