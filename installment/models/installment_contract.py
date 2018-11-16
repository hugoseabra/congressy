from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from base.models import EntityMixin


class InstallmentContract(EntityMixin, models.Model):
    OPEN_STATUS = 'open'
    CANCELLED_STATUS = 'cancelled'
    FULLY_PAID_STATUS = 'fully_paid'

    STATUS = (
        (OPEN_STATUS, "aberto"),
        (CANCELLED_STATUS, "cancelado"),
        (FULLY_PAID_STATUS, "quitado"),
    )

    class Meta:
        verbose_name = 'Contrato de Parcelamento'
        verbose_name_plural = 'Contratos de Parcelamento'

    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="criado",
    )

    modified = models.DateTimeField(
        auto_now=True,
        verbose_name="modificado",
    )

    subscription = models.ForeignKey(
        'gatheros_subscription.Subscription',
        on_delete=models.PROTECT,
        verbose_name='inscrição',
        related_name='installment_contracts',
        # Required
        blank=False,
        null=False,
    )

    liquid_amount = models.DecimalField(
        verbose_name="total líquido a pagar",
        # Required
        blank=False,
        null=False,
    )

    amount = models.DecimalField(
        verbose_name="total a pagar",
        # Required
        blank=False,
        null=False,
    )

    num_installments = models.PositiveIntegerField(
        verbose_name="número de parcelas",
        # Required
        blank=False,
        null=False,
    )

    expiration_day = models.PositiveIntegerField(
        verbose_name="vencimento todo dia",
        # Required
        blank=False,
        null=False,
        validators=[MaxValueValidator(31), MinValueValidator(1)],
    )

    limit_date = models.DateField(
        verbose_name="data limite de parcelamento",
        # Required
        blank=False,
        null=False,
    )

    minimum_amount_creation = models.DateField(
        verbose_name="montante mínimo para parcelamento",
        # Required
        blank=False,
        null=False,
        editable=False
    )

    minimum_amount = models.DecimalField(
        verbose_name="valor mínimo de parcelamento",
        # Required
        blank=False,
        null=False,
    )

    minimum_installment_amount = models.DecimalField(
        verbose_name="valor mínimo de parcela",
        # Required
        blank=False,
        null=False,
    )

    status = models.CharField(
        verbose_name="status",
        choices=STATUS,
        default=OPEN_STATUS,
        # Required
        blank=False,
        null=False,
    )
