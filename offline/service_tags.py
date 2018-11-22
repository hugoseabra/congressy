from .base import OfflineBase, EraserMixin


class ServiceTagsOffline(OfflineBase, EraserMixin):
    erase_list = [
        'service_tags.CustomServiceTag',
    ]
