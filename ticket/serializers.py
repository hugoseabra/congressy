from rest_framework import serializers

from core.serializers import FormSerializerMixin
from ticket.models import Ticket, Lot
from ticket.services import TicketService, LotService


class TicketSerializer(FormSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Ticket
        form = TicketService
        fields = '__all__'


class LotSerializer(FormSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Lot
        form = LotService
        fields = '__all__'
