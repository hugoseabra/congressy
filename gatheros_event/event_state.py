from gatheros_event.event_specifications import (
    EventVisible,
    EventPayable,
)

from gatheros_event.models import Event


class EventState(object):
    """
        Objetivo: Obter um evento e receber informações sobre o estado do mesmo.
    """

    def __init__(self, event: Event) -> None:
        self.event = event

    def is_public(self) -> bool:
        return EventVisible().is_satisfied_by(self.event) is True

    def is_private(self) -> bool:
        spec = EventVisible().not_specification()
        return spec.is_satisfied_by(self.event) is True

    def is_payable(self) -> bool:
        return EventPayable().is_satisfied_by(self.event) is True

    def is_free(self) -> bool:
        spec = EventPayable().not_specification()
        return spec.is_satisfied_by(self.event) is True
