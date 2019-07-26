from rest_framework import serializers

from core.serializers import FormSerializerMixin
from ticket.models import Ticket, Lot
from ticket.services import TicketService, TicketLotService


class TicketSerializer(FormSerializerMixin, serializers.ModelSerializer):
    num_lots = serializers.SerializerMethodField()
    num_subs = serializers.SerializerMethodField()

    display_name = serializers.ReadOnlyField()
    status = serializers.ReadOnlyField()

    class Meta:
        model = Ticket
        form = TicketService
        fields = '__all__'

    # noinspection PyMethodMayBeStatic
    def get_num_lots(self, obj):
        return Lot.objects.filter(ticket_id=obj.pk).count()

    # noinspection PyMethodMayBeStatic
    def get_num_subs(self, obj):
        return obj.num_subs


class TicketLotSerializer(FormSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Lot
        form = TicketLotService
        fields = '__all__'
