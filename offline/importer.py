from .base import Base, EraserMixin


class ImporterOffline(Base, EraserMixin):
    erase_list = [
        'importer.CSVFileConfig',
    ]
