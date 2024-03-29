# pylint: disable=C0111,W0612
from django.apps import AppConfig


class GatherosSubscriptionConfig(AppConfig):
    name = 'gatheros_subscription'
    verbose_name = 'Inscrições'

    # noinspection PyUnresolvedReferences
    def ready(self):
        import gatheros_subscription.signals
