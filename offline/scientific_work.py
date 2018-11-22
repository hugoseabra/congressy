from .base import OfflineBase, EraserMixin


class ScientificWorkOffline(OfflineBase, EraserMixin):
    erase_list = [
        'scientific_work.Work',
        'scientific_work.WorkConfig',
        'scientific_work.Author',
        'scientific_work.AreaCategory',
    ]
