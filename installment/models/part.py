from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from base.models import EntityMixin


class Part(EntityMixin, models.Model):
    class Meta:
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
