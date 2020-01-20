"""
    Esses helpers tem como objetivo identificar o tipo do evento:

        - Grátis
        - Pago

    Além de também mudar o tipo do evento e aplicar as configuração das features
    disponiveis de acordo com o tipo em si

"""

from gatheros_event.event_specifications import (
    EventSubscribable,
    LotSubscribable,
)
from gatheros_event.models import Event


def is_event_subscribable(event: Event):
    return EventSubscribable().is_satisfied_by(event)


def has_enabled_private_lots(event: Event):
    has_lots = False

    lot_spec = LotSubscribable()
    for lot in event.lots.filter(active=True, private=True, ):
        if lot_spec.is_satisfied_by(lot) is True:
            has_lots = True
            break

    return has_lots is True
