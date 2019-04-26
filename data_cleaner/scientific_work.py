from .base import DataCleanerBase, EraserMixin


class ScientificWorkDataCleaner(DataCleanerBase, EraserMixin):
    erase_list = [
        'scientific_work.Work',
        'scientific_work.WorkConfig',
        'scientific_work.Author',
        'scientific_work.AreaCategory',
    ]
