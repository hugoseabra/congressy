"""
Domínio de controle de pendências financeiras da plataforma.
"""
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from gatheros_subscription.models import Lot, Subscription


class Debt(models.Model):
    """
    Determina uma pendência financeira de um inscrição enquanto ela estava em
    lote. A pendência pode ser: da própria inscrição,, atividade extra ou
    opcional.
    """

    class Meta:
        verbose_name = 'pendência'
        verbose_name_plural = 'pendências'
        unique_together = (
            ('lot', 'subscription'),
        )

    DEBT_TYPE_SUBSCRIPTION = 'subscription'
    DEBT_TYPE_SERVICE = 'service'
    DEBT_TYPE_PRODUCT = 'product'

    DEBT_TYPES = (
        (DEBT_TYPE_SUBSCRIPTION, 'Inscrição'),
        (DEBT_TYPE_SERVICE, 'Atividade Extra'),
        (DEBT_TYPE_PRODUCT, 'Opcional'),
    )

    DEBT_STATUS_DEBT = 'debt'
    DEBT_STATUS_PAID = 'paid'
    DEBT_STATUS_CREDIT = 'credit'

    DEBT_STATUS_CHOICES = (
        (DEBT_STATUS_DEBT, 'pendente'),
        (DEBT_STATUS_PAID, 'pago'),
        (DEBT_STATUS_CREDIT, 'com crédito'),
    )

    lot = models.ForeignKey(
        Lot,
        on_delete=models.PROTECT,
        related_name='debts',
        editable=False,
    )

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='debts',
    )

    type = models.CharField(
        max_length=20,
        default=DEBT_TYPE_SUBSCRIPTION,
        choices=DEBT_TYPES,
    )

    status = models.CharField(
        max_length=20,
        default=DEBT_STATUS_DEBT,
        choices=DEBT_STATUS_CHOICES,
        null=True,
        blank=True,
        verbose_name='status',
        help_text='qual a situação atual da pendência',
    )

    amount = models.DecimalField(
        decimal_places=2,
        max_digits=11,
        null=True,  # REMOVER
        blank=True,  # REMOVER
        verbose_name='valor',
        help_text='valor cobrado ao comprador',
    )

    liquid_amount = models.DecimalField(
        decimal_places=2,
        max_digits=11,
        null=True,  # REMOVER
        blank=True,  # REMOVER
        verbose_name='valor líquido',
        help_text='valor que o organizador irá receber',
    )

    installments = models.PositiveIntegerField(
        default=1,
        verbose_name='número de parcelas',
        help_text='número de parcelas da compra',
    )

    installment_amount = models.DecimalField(
        decimal_places=2,
        max_digits=11,
        null=True,
        blank=True,
        verbose_name='valor da parcela',
    )

    installment_interests_amount = models.DecimalField(
        decimal_places=2,
        max_digits=11,
        null=True,  # REMOVER
        blank=True,  # REMOVER
        verbose_name='valor dos juros do parcelamento',
    )

    def __str__(self):
        return '{} - {} ({})'.format(
            self.get_type_display(),
            self.subscription.pk,
            self.get_status_display(),
        )

    def save(self, *args, **kwargs):
        if self._state.adding is True:
            self.lot = self.subscription.lot

        super().save(*args, **kwargs)


class DebtConfig(models.Model):
    """
    Configuração de pendências reúne as informações importantes de como o lote
    estava configurado no momento de criação da pendência finaceira.
    """

    class Meta:
        verbose_name = 'configuração de pendência'
        verbose_name_plural = 'configurações de pendências'

    transfer_tax = models.BooleanField(
        verbose_name='transferir taxa',
        help_text='se taxa foi transferida ao participante',
    )

    total_installments = models.PositiveIntegerField(
        default=1,
        verbose_name='total de parcelas',
        help_text='total possível para parcelamento',
    )

    free_installments = models.PositiveIntegerField(
        default=1,
        verbose_name='parcelas livre de juros',
        help_text='número de parcelas em que o organizador absorveu os juros',
    )

    interests_rate = models.DecimalField(
        max_digits=11,
        decimal_places=3,
        verbose_name='percentual de taxa de juros de parcelamento',
    )

    debt = models.OneToOneField(
        Debt,
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name='pendência',
        related_name='config',
    )

    def __str__(self):
        return '{} - {}'.format(self.debt.type, self.debt.subscription.pk)


@receiver(post_save, sender=Debt)
def _debt_create_config_post_save(instance, created, raw, **_):
    if raw is True or created is False:
        return

    lot = instance.lot

    DebtConfig.objects.create(
        debt=instance,
        transfer_tax=lot.transfer_tax,
        interests_rate=Decimal(settings.CONGRESSY_INSTALLMENT_INTERESTS_RATE),
        total_installments=lot.installment_limit,
        free_installments=lot.num_install_interest_absortion,
    )


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
