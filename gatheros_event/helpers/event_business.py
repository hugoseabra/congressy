"""
    Esses helpers tem como objetivo identificar o tipo do evento:

        - Grátis
        - Pago

    Além de também mudar o tipo do evento e aplicar as configuração das features
    disponiveis de acordo com o tipo em si

"""

from gatheros_event.event_state import EventState
from gatheros_event.models import Event


def is_free_event(event: Event):
    if not isinstance(event, Event):
        raise Exception("{} '{}' não é uma instancia de Event".format(
            event,
            event.__class__,
        ))

    return EventState(event).is_free()


def is_paid_event(event: Event):
    if not isinstance(event, Event):
        raise Exception("{} '{}' não é uma instancia de Event".format(
            event,
            event.__class__,
        ))

    return EventState(event).is_payable()
