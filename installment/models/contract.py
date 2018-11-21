from datetime import timedelta

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from base.models import EntityMixin, RuleChecker, RuleIntegrityError


class MinimumAmountWriteOnce(RuleChecker):

    def check(self, model_instance, *args, **kwargs):

        if model_instance.__original_minimum_amount_creation and \
                model_instance.minimum_amount_creation != \
                model_instance.__original_minimum_amount_creation:
            raise RuleIntegrityError(
                'O campo \'minimum_amount_creation\' não é'
                ' editavel')

        if model_instance.__original_minimum_amount and \
                model_instance.minimum_amount != \
                model_instance.__original_minimum_amount:
            raise RuleIntegrityError('O campo \'minimum_amount\' não é'
                                     ' editavel')


class OnlyOneOpenContract(RuleChecker):
    def check(self, model_instance, *args, **kwargs):
        sub = model_instance.subscription

        if model_instance.is_new is False:
            return

        contract_qs = \
            sub.installment_contracts.filter(status=Contract.OPEN_STATUS)

        if contract_qs.count() > 0:
            raise RuleIntegrityError(
                'Não é possível criar mais de um contrato ativo.'
            )


class Contract(EntityMixin, models.Model):
    rule_instances = [
        MinimumAmountWriteOnce,
        OnlyOneOpenContract
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
        self.__original_minimum_amount = self.minimum_amount

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
        blank=True,
        null=False,
    )

    minimum_amount_creation = models.DecimalField(
        verbose_name="valor mínimo para habilitar parcelamento",
        decimal_places=2,
        max_digits=11,
        # Required
        blank=True,
        null=False,
    )

    minimum_amount = models.DecimalField(
        verbose_name="valor mínimo por parcela",
        decimal_places=2,
        max_digits=11,
        # Required
        blank=True,
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

    @property
    def is_new(self):
        return self._meta.adding is True

    def save(self, **kwargs):

        if self.minimum_amount_creation is None:
            self.minimum_amount_creation = \
                settings.CONGRESSY_MINIMUM_AMOUNT_TO_ALLOW_INSTALLMENTS

        if self.minimum_amount is None:
            self.minimum_amount_creation = \
                settings.CONGRESSY_MINIMUM_AMOUNT_FOR_INSTALLMENTS

        if self.limit_date is None:
            self.limit_date = self.subscription.event.date_start - timedelta(
                days=2)

        super().save(kwargs)
