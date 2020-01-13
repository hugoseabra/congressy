from django.apps import AppConfig


class PaymentDebtConfig(AppConfig):
    name = 'payment_debt'
    verbose_name = 'Pendência'
    verbose_name_plural = 'Pendênciass'

    # noinspection PyUnresolvedReferences
    def ready(self):
        import payment_debt.signals
