"""
    Esses helpers tem como objetivo identificar o tipo do evento:

        - Grátis
        - Pago

    Além de também mudar o tipo do evento e aplicar as configuração das features
    disponiveis de acordo com o tipo em si

"""

from gatheros_event.event_specifications import EventSubscribable
from gatheros_event.models import Event


def is_event_subscribable(event: Event):
    return EventSubscribable().is_satisfied_by(event)
