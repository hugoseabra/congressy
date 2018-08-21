from datetime import datetime

from gatheros_event.models import Event
from .mixins import EventSpecificationMixin


class HasSubscriptions(EventSpecificationMixin):
    """
        Essa especificação informa se o evento possui alguma inscrição valida
        realizada
    """

    def is_satisfied_by(self, event: Event):
        super().is_satisfied_by(event)
        for lot in event.lots.all():
            valid_subs = self._get_valid_subs_in_lot(lot)
            if valid_subs and valid_subs.count() > 0:
                return True
        
        return False
