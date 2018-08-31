from gatheros_event.models import Event
from .mixins import (
    EventCompositeSpecificationMixin,
)


class EventPublishable(EventCompositeSpecificationMixin):
    """
        Essa especificação informa se o evento é capaz de ser publicado para que
        seu hotsite possa disponibilizar inscrições. Para isso o evento deve
        possuir as seguintes condições:

        - Lotes que estão ou serão vigentes no futuro.
        - Caso o evento seja pago, tenha opcional pago ou lote pago:
            - Deve possuir dados bancarios cadastrados
        - Deve possuir uma descrição do evento
        - TODO: Caso seja cientifico:
            - ????
            


    """

    def is_satisfied_by(self, event: Event):
        super().is_satisfied_by(event)
        return False


class EventAllowsSubscriptions(EventCompositeSpecificationMixin):
    pass