from datetime import datetime

from gatheros_event.models import Event
from gatheros_subscription.models import Lot
from .mixins import EventCompositeSpecificationMixin, \
    LotCompositeSpecificationMixin


class EventSubscribable(EventCompositeSpecificationMixin):
    """
        Essa especificação informa se o evento possui algum lote quer permita
        que ele seja capaz de receber inscrições no presente ou futuro
    """

    def is_satisfied_by(self, event: Event):
        super().is_satisfied_by(event)

        for lot in event.lots.filter(active=True):

            lot_spec = LotSubscribable()
            if lot_spec.is_satisfied_by(lot):
                return True

        return False


class LotSubscribable(LotCompositeSpecificationMixin):
    """
        Essa especificação informa se o lote possui seja capaz de receber
        inscrições no presente ou futuro
    """

    def is_satisfied_by(self, lot: Lot):
        super().is_satisfied_by(lot)
        now = datetime.now()
        if now < lot.date_end:
            return True

        return False
