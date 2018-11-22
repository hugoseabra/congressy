from .base import Base, EraserMixin


class ServiceTagsOffline(Base, EraserMixin):
    erase_list = [
        'service_tags.CustomServiceTag',
    ]
