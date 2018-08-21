from gatheros_event.event_specifications import (
    EventHasSubscriptions,
    EventSubscribable,
)
from gatheros_event.models import Event
from .mixins import EventAndSpecificationMixin


class ClosedWithNoAudience(EventAndSpecificationMixin):

    def __init__(self):
        one = EventSubscribable().not_specification()
        other = EventHasSubscriptions().not_specification()

        super().__init__(one, other)


class ClosedWithAudience(EventAndSpecificationMixin):

    def __init__(self):
        one = EventSubscribable().not_specification()
        other = EventSubscribable()

        super().__init__(one, other)


class OpenWithNoAudience(EventAndSpecificationMixin):

    def __init__(self):
        one = EventSubscribable()
        other = EventHasSubscriptions().not_specification()
        super().__init__(one, other)


class OpenWithAudience(EventAndSpecificationMixin):

    def __init__(self):
        one = EventSubscribable()
        other = EventSubscribable()
        super().__init__(one, other)
