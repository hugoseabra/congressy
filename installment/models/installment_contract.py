from datetime import datetime

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from base.models import EntityMixin, RuleChecker, RuleIntegrityError


class MinimumAmountCreationWriteOnce(RuleChecker):

    def check(self, model_instance, *args, **kwargs):

        if model_instance.minimum_amount and model_instance.minimum_amount_creation is None:
            model_instance.minimum_amount_creation = datetime.now().date()

        elif model_instance.minimum_amount_creation is not None and \
                model_instance.minimum_amount_creation != \
                model_instance.__original_minimum_amount_creation:
            raise RuleIntegrityError('O campo \'minimum_amount_creation\' não é'
                                     ' editavel')


class InstallmentContract(EntityMixin, models.Model):

    rule_instances = [
        MinimumAmountCreationWriteOnce
    ]

    OPEN_STATUS = 'open'
    CANCELLED_STATUS = 'cancelled'
    FULLY_PAID_STATUS = 'fully_paid'

    STATUS = (
        (OPEN_STATUS, "aberto"),
        (CANCELLED_STATUS, "cancelado"),
        (FULLY_PAID_STATUS, "quitado"),
    )

    __original_minimum_amount_creation = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_minimum_amount_creation = self.minimum_amount_creation

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
        decimal_places=2,
        max_digits=11,
        # Required
        blank=False,
        null=False,
    )

    amount = models.DecimalField(
        verbose_name="total a pagar",
        decimal_places=2,
        max_digits=11,
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
    )

    minimum_amount = models.DecimalField(
        verbose_name="valor mínimo de parcelamento",
        decimal_places=2,
        max_digits=11,
        # Required
        blank=False,
        null=False,
    )

    minimum_installment_amount = models.DecimalField(
        verbose_name="valor mínimo de parcela",
        decimal_places=2,
        max_digits=11,
        # Required
        blank=False,
        null=False,
    )

    status = models.CharField(
        verbose_name="status",
        choices=STATUS,
        default=OPEN_STATUS,
        max_length=20,
        # Required
        blank=False,
        null=False,
    )
