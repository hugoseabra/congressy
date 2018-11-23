from .base import DataCleanerBase, EraserMixin


class ServiceTagsDataCleaner(DataCleanerBase, EraserMixin):
    erase_list = [
        'service_tags.CustomServiceTag',
    ]
