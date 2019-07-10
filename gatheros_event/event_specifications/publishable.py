from gatheros_event.models import Event
from .mixins import (
    EventCompositeSpecificationMixin,
)
from .payable import EventPayable, OrganizationHasBanking


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

        if not hasattr(event, 'info'):
            return False

        if not event.info.description:
            return False

        if EventPayable().is_satisfied_by(event):
            org = event.organization
            if not OrganizationHasBanking().is_satisfied_by(org):
                return False

        return True

    @staticmethod
    def get_reason(event: Event):

        if not hasattr(event, 'info') or not event.info.description:
            return 'Seu evento não possui uma descrição. ' \
                   'Veja os dados da pagina do evento!'

        if EventPayable().is_satisfied_by(event):
            org = event.organization
            if not OrganizationHasBanking().is_satisfied_by(org):
                return 'Seu evento é pago e não possui dados bancarios para ' \
                       'receber pagamentos. Veja os detalhes da sua ' \
                       'organização!'

        return ''
