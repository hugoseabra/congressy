from datetime import datetime

from gatheros_event.models import Event
from .mixins import EventSpecificationMixin


class Subscribable(EventSpecificationMixin):
    """
        Essa especificação informa se o evento possui algum lote quer permita
        que ele seja capaz de receber inscrições no presente ou futuro
    """

    def is_satisfied_by(self, event: Event):
        super().is_satisfied_by(event)

        now = datetime.now()
        for lot in event.lots.filter(active=True):

            if now < lot.date_end:
                return True

        return False
