from django.db import models

from gatheros_subscription.models import Lot, Subscription
from payment.models import Transaction


class Payment(models.Model):
    """
    Registro de pagamento para uma determinada inscrição enquanto ela estava
    em um determinado lote.
    """

    class Meta:
        verbose_name = 'pagamento'
        verbose_name_plural = 'pagamentos'

    CASH_TYPE_BOLETO = 'boleto'
    CASH_TYPE_CREDIT_CARD = 'credit_card'
    CASH_TYPE_DEBIT_CARD = 'debit_card'
    CASH_TYPE_PAYCHECK = 'paycheck'
    CASH_TYPE_BANK_DEPOSIT = 'bank_deposit'
    CASH_TYPE_MONEY = 'money'
    CASH_TYPE_TRANSFER = 'bank_transfer'

    CASH_TYPES = (
        (CASH_TYPE_BOLETO, 'Boleto'),
        (CASH_TYPE_CREDIT_CARD, 'Cartão de Crédito'),
        (CASH_TYPE_DEBIT_CARD, 'Cartão de Débito'),
        (CASH_TYPE_PAYCHECK, 'Cheque'),
        (CASH_TYPE_BANK_DEPOSIT, 'Depósito'),
        (CASH_TYPE_MONEY, 'Dinheiro'),
        (CASH_TYPE_TRANSFER, 'Transferência Bancária'),
    )

    lot = models.ForeignKey(
        Lot,
        on_delete=models.PROTECT,
        related_name='payments',
        editable=False,
    )

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    cash_type = models.CharField(
        max_length=30,
        choices=CASH_TYPES,
    )

    manual = models.BooleanField(
        default=False,
        verbose_name='lançamento manual',
    )

    manual_author = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='author do lançamento manual',
    )

    amount = models.DecimalField(
        decimal_places=2,
        max_digits=11,
        null=True,
        blank=True,
        verbose_name='valor',
        help_text='valor cobrado ao comprador',
    )

    paid = models.BooleanField(
        default=False,
        verbose_name='pago',
    )

    transaction = models.OneToOneField(
        to=Transaction,
        on_delete=models.CASCADE,
        related_name='payment',
        null=True,
        blank=True,
        editable=False,
    )

    def __str__(self):
        string = '{} - $ {}'.format(
            self.get_cash_type_display(),
            self.amount,
        )
        if self.manual_author:
            string += '(manual: {})'.format(self.manual_author)

        return string

    def save(self, *args, **kwargs):
        if self._state.adding is True:
            self.lot = self.subscription.lot

        return super().save(*args, **kwargs)
