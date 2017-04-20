from django.apps import AppConfig


class GatherosSubscriptionConfig(AppConfig):
    name = 'gatheros_subscription'
    verbose_name = 'Inscrições'

    def ready(self):
        import gatheros_subscription.signals