# pylint: disable=C0111,W0612
from django.apps import AppConfig


class GatherosEventConfig(AppConfig):
    name = 'gatheros_event'
    verbose_name = 'Eventos'

    # noinspection PyUnresolvedReferences
    def ready(self):
        import gatheros_event.signals
