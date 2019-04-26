# pylint: disable=C0111,W0612
from django.apps import AppConfig


class InstallmentConfig(AppConfig):
    name = 'installment'
    verbose_name = 'Parcelamentos'

    # noinspection PyUnresolvedReferences
    def ready(self):
        import installment.signals

