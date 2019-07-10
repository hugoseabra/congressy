from gatheros_event.models import Event
from ticket.models import Lot
from .mixins import (
    EventCompositeSpecificationMixin,
)


class EventSubscribable(EventCompositeSpecificationMixin):
    """
        Essa especificação informa se o evento possui algum lote quer permita
        que ele seja capaz de receber inscrições no presente ou futuro
    """

    def is_satisfied_by(self, event: Event):
        super().is_satisfied_by(event)

        if event.running is False:
            return False

        lots = Lot.objects.filter(
            ticket__event_id=event.pk,
            ticket__active=True,
        )

        if lots.count() == 0:
            return False

        for lot in lots:
            if lot.subscribable is True:
                return True

        return False
