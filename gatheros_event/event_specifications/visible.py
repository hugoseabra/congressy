from datetime import datetime

from core.util.date import DateTimeRange
from gatheros_event.models import Event
from gatheros_subscription.models import Lot
from .mixins import EventCompositeSpecificationMixin, \
    LotCompositeSpecificationMixin


class EventVisible(EventCompositeSpecificationMixin):
    """
        Essa especificação informa se o evento possui algum lote quer permita
        que ele seja visivel e possa receber inscrições no presente ou futuro
    """

    def is_satisfied_by(self, event: Event):
        super().is_satisfied_by(event)

        for lot in event.lots.filter(active=True):

            lot_spec = LotVisible()
            if lot_spec.is_satisfied_by(lot):
                return True

        return False


class LotVisible(LotCompositeSpecificationMixin):
    """
        Essa especificação informa se o lote é visivel e  seja capaz de receber
        inscrições no presente ou futuro
    """

    def is_satisfied_by(self, lot: Lot):
        super().is_satisfied_by(lot)

        if lot.private:
            return False

        now = datetime.now()
        # Verificação se o lote está dentro do prazo ativo
        lot_range = DateTimeRange(start=lot.date_start, stop=lot.date_end)
        if now not in lot_range:
            return False

        # Verificação de limite de lote
        total_subs_in_lot = self._get_valid_subs_in_lot(lot)
        if total_subs_in_lot and total_subs_in_lot >= lot.limit:
            return False

        return True
