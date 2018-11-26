from django.conf import settings
from django.db import models

from base.models import EntityMixin, RuleChecker, RuleIntegrityError


class MinimumAmount(RuleChecker):

    def check(self, model_instance, *args, **kwargs):
        if model_instance.amount \
                < settings.CONGRESSY_MINIMUM_AMOUNT_FOR_INSTALLMENTS:
            raise RuleIntegrityError(
                'Valor da parcela abaixo do mínimo para '
                'permitir parcelamento de inscrição '
            )


class Part(EntityMixin, models.Model):

    rule_instances = [
        MinimumAmount,
    ]

    class Meta:
        ordering = ['expiration_date']
        verbose_name = 'Parcela de Contrato'
        verbose_name_plural = 'Parcelas de Contrato'

    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="criado",
    )

    modified = models.DateTimeField(
        auto_now=True,
        verbose_name="modificado",
    )

    contract = models.ForeignKey(
        'installment.Contract',
        on_delete=models.CASCADE,
        verbose_name='parcela de inscrição',
        related_name='installment_parts',
        # Required
        blank=False,
        null=False,
    )

    transaction = models.OneToOneField(
        'payment.Transaction',
        on_delete=models.DO_NOTHING,
        verbose_name='transação da parcela',
        related_name='part_transaction',
        # Not required
        blank=True,
        null=True,
    )

    amount = models.DecimalField(
        verbose_name="valor",
        decimal_places=2,
        max_digits=11,
        # Required
        blank=False,
        null=False,
    )

    expiration_date = models.DateField(
        verbose_name="vencimento",
        # Required
        blank=True,
        null=False,
    )

    installment_number = models.PositiveIntegerField(
        verbose_name="número da parcela",
        # Required
        blank=False,
        null=False,
    )

    paid = models.BooleanField(
        verbose_name="pago",
        default=False,
    )
