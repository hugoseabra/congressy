from .base import Base, EraserMixin


class AssociateOffline(Base, EraserMixin):
    erase_list = [
        'associate.Associate',
    ]
