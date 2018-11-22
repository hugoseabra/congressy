from .base import OfflineBase, EraserMixin


class AssociateOffline(OfflineBase, EraserMixin):
    erase_list = [
        'associate.Associate',
    ]
