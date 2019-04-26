from .base import DataCleanerBase, EraserMixin


class AssociateDataCleaner(DataCleanerBase, EraserMixin):
    erase_list = [
        'associate.Associate',
    ]
