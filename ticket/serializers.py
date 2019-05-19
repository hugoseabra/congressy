from rest_framework import serializers

from core.serializers import FormSerializerMixin
from gatheros_subscription.models import Subscription
from ticket.models import Ticket, Lot
from ticket.services import TicketService, LotService


class TicketSerializer(FormSerializerMixin, serializers.ModelSerializer):
    lot_count = serializers.SerializerMethodField()

    display_name = serializers.ReadOnlyField()
    status = serializers.ReadOnlyField()

    class Meta:
        model = Ticket
        form = TicketService
        fields = '__all__'

    # noinspection PyMethodMayBeStatic
    def get_lot_count(self, obj):
        return Lot.objects.filter(
            ticket=obj,
        ).count()


class LotSerializer(FormSerializerMixin, serializers.ModelSerializer):

    class Meta:
        model = Lot
        form = LotService
        fields = '__all__'
