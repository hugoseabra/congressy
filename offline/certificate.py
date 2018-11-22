from .base import OfflineBase, EraserMixin


class CertificateOffline(OfflineBase, EraserMixin):
    erase_list = [
        'certificate.Certificate',
    ]
