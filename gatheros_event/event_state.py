import abc

from django.db.models import QuerySet

from gatheros_event.models import Event


class EventState(abc.ABC):
    """
        Interface usada para descrever estados de eventos.
        Veja `EventPrivacy`, `EventBusiness`
    """

    def __init__(self, event: Event) -> None:
        self.event = event

    @abc.abstractmethod
    def get_state(self) -> str:
        pass


class EventPrivacyState(EventState):
    """
    Objetivo: Obter um evento e receber informações sobre o estado de
    privacidade do mesmo.

    Caso o evento ainda tem algum lote disponivel, sua privacidade é definida
    através destes lotes disponiveis conforme:

        Privado:
            * Todos os lotes disponíveis devem ser configurado como 'privado';

        Público:
            * Deve ter pelo menos um Lote disponível e configurado como
              'não-privado';

    Caso não tenha nenhum lote disponivel, a privacidade é definida analisando
    todos os lotes antigos observando as regas acima mas também levando em
    consideração se algum lote teve inscrição.
    """

    PRIVATE = 'private'
    PUBLIC = 'public'

    def get_state(self) -> str:

        available_lots = self._get_available_lots()

        if len(available_lots) > 0:

            # Has at least one available lot
            for lot in available_lots:

                if not lot.private:
                    return self.PUBLIC

            return self.PRIVATE

        # Has no available lot
        all_lots = self._get_all_lots()

        for lot in all_lots:
            if not lot.private and lot.subscriptions.filter(
                    completed=True,
                    test_subscription=False,
            ).count() > 0:
                return self.PUBLIC

        return self.PRIVATE

    def _get_available_lots(self) -> list:
        all_lots = self._get_all_lots()

        return [lot for lot in all_lots if lot.status == lot.LOT_STATUS_RUNNING]

    def _get_all_lots(self) -> QuerySet:
        return self.event.lots.all()
