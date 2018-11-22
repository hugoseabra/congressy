from .base import Base, EraserMixin


class CertificateOffline(Base, EraserMixin):
    erase_list = [
        'certificate.Certificate',
    ]
