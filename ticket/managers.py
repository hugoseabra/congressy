from base.managers import Manager
from ticket.models import Lot


class TicketManager(Manager):
    class Meta:
        model = Lot
        fields = '__all__'


class LotManager(Manager):
    class Meta:
        model = Lot
        fields = '__all__'
