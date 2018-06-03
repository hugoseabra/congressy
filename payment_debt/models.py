"""
Domínio de controle de pendências financeiras da plataforma.
"""
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from gatheros_subscription.models import Subscription


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
            ('type', 'subscription'),
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

    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='criado em'
    )

    def __str__(self):
        return '{} - {} ({})'.format(
            self.pk,
            self.get_type_display(),
            self.subscription.pk,
            self.get_status_display(),
        )

    @property
    def paid(self):
        return self.status == self.DEBT_STATUS_PAID

    @property
    def in_debt(self):
        return self.status == self.DEBT_STATUS_DEBT

    @property
    def has_credit(self):
        return self.status == self.DEBT_STATUS_CREDIT


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

    lot = instance.subscription.lot

    DebtConfig.objects.create(
        debt=instance,
        transfer_tax=lot.transfer_tax,
        interests_rate=Decimal(settings.CONGRESSY_INSTALLMENT_INTERESTS_RATE),
        total_installments=lot.installment_limit,
        free_installments=lot.num_install_interest_absortion,
    )
