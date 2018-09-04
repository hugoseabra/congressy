from gatheros_event.models import Event
from .mixins import (
    EventCompositeSpecificationMixin,
)
from .payable import EventPayable, OrganizationHasBanking
from .subscribable import EventSubscribable


class EventPublishable(EventCompositeSpecificationMixin):
    """
        Essa especificação informa se o evento é capaz de ser publicado para que
        seu hotsite possa disponibilizar inscrições. Para isso o evento deve
        possuir as seguintes condições:

        - Lotes que estão ou serão vigentes no futuro
        - Deve possuir uma descrição do evento
        - Caso o evento seja pago:
            - Deve possuir dados bancarios cadastrados
    """

    def is_satisfied_by(self, event: Event):
        super().is_satisfied_by(event)

        visibility_spec = EventSubscribable().is_satisfied_by(event)
        org = event.organization
        payable_spec = EventPayable().is_satisfied_by(event)
        banking_spec = OrganizationHasBanking().is_satisfied_by(org)

        if not visibility_spec:
            return False

        if not event.info.description:
            return False

        if payable_spec and not banking_spec:
            return False

        return True
