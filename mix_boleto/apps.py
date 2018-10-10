# pylint: disable=C0111,W0612
from django.apps import AppConfig


class MixBoletoConfig(AppConfig):
    name = 'mix_boleto'
    verbose_name = 'Boletos MixEvents'

    # noinspection PyUnresolvedReferences
    def ready(self):
        import mix_boleto.signals
