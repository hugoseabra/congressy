from django.apps import AppConfig


class PartnerConfig(AppConfig):
    name = 'partner'
    verbose_name = 'Parceiros'

    # noinspection PyUnresolvedReferences
    def ready(self):
        import partner.signals


