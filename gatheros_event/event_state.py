import abc

from gatheros_event.models import Event


class EventState(abc.ABC):

    def __init__(self, event: Event) -> None:
        self.event = event

    @abc.abstractmethod
    def get_state(self):
        pass
