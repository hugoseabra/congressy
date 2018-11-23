from .base import DataCleanerBase, EraserMixin


class CertificateDataCleaner(DataCleanerBase, EraserMixin):
    erase_list = [
        'certificate.Certificate',
    ]
