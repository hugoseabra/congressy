from .base import DataCleanerBase, EraserMixin


class DjangoContribDataCleaner(DataCleanerBase, EraserMixin):
    erase_list = [
        'sessions.Session',
    ]
