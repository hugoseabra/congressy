from gatheros_event.models import Event
from ticket.models import Ticket
from .mixins import EventCompositeSpecificationMixin


class EventVisible(EventCompositeSpecificationMixin):
    """
        Essa especificação informa se o evento possui algum lote quer permita
        que ele seja visivel e possa receber inscrições no presente ou futuro
    """

    def is_satisfied_by(self, event: Event):
        super().is_satisfied_by(event)

        qs = Ticket.objects.filter(event_id=event.pk, private=False)
        return len([t.pk for t in qs if t.running is True]) > 0
