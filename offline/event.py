from .base import Base, EraserMixin


class EventOffline(Base, EraserMixin):
    erase_list = [
        'gatheros_event.Invitation',
    ]
