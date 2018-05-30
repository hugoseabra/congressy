from django.db import models

from payment_debt.models import Payment


class Provider(models.Model):
    """
    Define uma estrutura de registro de pagamento para uma determinada
    inscrição enquanto ela estava em um determinado lote.
    """

    class Meta:
        verbose_name = 'provedor de transação'
        verbose_name_plural = 'provedores de transação'

    PROVIDER_TYPE_PAGARME = 'pagarme'

    PROVIDER_TYPES = (
        (PROVIDER_TYPE_PAGARME, 'Pagar.me'),
    )

    provider_type = models.CharField(
        max_length=10,
        default=PROVIDER_TYPE_PAGARME,
        choices=PROVIDER_TYPES,
    )

    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name='pagamento',
        related_name='provider',
    )
