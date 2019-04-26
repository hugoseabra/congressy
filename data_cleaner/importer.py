from .base import DataCleanerBase, EraserMixin


class ImporterDataCleaner(DataCleanerBase, EraserMixin):
    erase_list = [
        'importer.CSVFileConfig',
    ]
