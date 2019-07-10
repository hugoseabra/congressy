from gatheros_event.models import Event
from ticket.models import Lot
from .mixins import (
    EventCompositeSpecificationMixin,
    LotCompositeSpecificationMixin,
)


class EventHasSubscriptions(EventCompositeSpecificationMixin):
    """
        Essa especificação informa se o evento possui alguma inscrição valida
        realizada
    """

    def is_satisfied_by(self, event: Event):
        super().is_satisfied_by(event)

        for lot in Lot.objects.filter(ticket__event_id=event.pk):
            lot_spec = LotHasSubscriptions()
            if lot_spec.is_satisfied_by(lot):
                return True

        return False


class LotHasSubscriptions(LotCompositeSpecificationMixin):
    """
        Essa especificação informa se o evento possui alguma inscrição valida
        realizada
    """

    def is_satisfied_by(self, lot: Lot):
        super().is_satisfied_by(lot)
        valid_subs = self._get_valid_subs_in_lot(lot)
        return valid_subs.count() > 0
