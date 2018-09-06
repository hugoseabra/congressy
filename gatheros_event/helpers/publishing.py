from gatheros_event.event_specifications import EventPublishable
from gatheros_event.models import Event


def event_is_publishable(event: Event):
    spec = EventPublishable().is_satisfied_by(event)

    if not spec:
        return False

    return True


def get_unpublishable_reason(event: Event):
    return EventPublishable().get_reason(event)
