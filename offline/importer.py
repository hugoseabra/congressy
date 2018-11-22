from .base import OfflineBase, EraserMixin


class ImporterOffline(OfflineBase, EraserMixin):
    erase_list = [
        'importer.CSVFileConfig',
    ]
