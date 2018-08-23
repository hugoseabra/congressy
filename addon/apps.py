# pylint: disable=C0111,W0612
from django.apps import AppConfig


class AddonConfig(AppConfig):
    name = 'addon'
    verbose_name = 'Opcionais'

    # noinspection PyUnresolvedReferences
    def ready(self):
        import addon.signals
