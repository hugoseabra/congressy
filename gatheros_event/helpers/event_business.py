"""
    Esses helpers tem como objetivo identificar o tipo do evento:

        - Grátis
        - Pago

    Além de também mudar o tipo do evento e aplicar as configuração das features
    disponiveis de acordo com o tipo em si

"""

from gatheros_event.event_state import EventState, EventPayable
from gatheros_event.models import Event
from gatheros_event.event_specifications import Saleable


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


def removing_saleable_cause_feature_change(event: Event, candidate,
                                           candidate_type) -> bool:
    if not Saleable().is_satisfied_by(candidate):
        raise Exception(
            "{} '{}' não é uma instancia capaz de ser vendida".format(
                candidate,
                candidate.__class__,
            ))

    return not EventPayable(exclude=candidate,
                            exclude_type=candidate_type).is_satisfied_by(event)
