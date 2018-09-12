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

        if event.is_scientific:

            if not hasattr(event, 'work_config'):
                return False

            if not event.work_config.is_configured:
                return False

        return True

    @staticmethod
    def get_reason(event: Event):

        visibility_spec = EventSubscribable().is_satisfied_by(event)
        org = event.organization
        payable_spec = EventPayable().is_satisfied_by(event)
        banking_spec = OrganizationHasBanking().is_satisfied_by(org)

        if not visibility_spec:
            return 'Seu evento não está visivel.' \
                   ' Veja a situação dos seus lotes!'

        if not event.info.description:
            return 'Seu evento não possui uma descrição. ' \
                   'Veja os dados da pagina do evento!'

        if payable_spec and not banking_spec:
            return 'Seu evento é pago e não possui dados bancarios para ' \
                   'receber pagamentos. Veja os detalhes da sua organização!'

        if event.is_scientific:
            if not event.work_config and event.work_config.is_configured:
                return 'Você ainda não configurou seu evento para receber ' \
                       'inscrições cientificas!'

        return ''
