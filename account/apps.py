from django.apps import AppConfig


class AccountConfig(AppConfig):
    name = 'account'
    verbose_name = 'Conta'

    # noinspection PyUnresolvedReferences
    def ready(self):
        import account.signals
