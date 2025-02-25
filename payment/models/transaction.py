# pylint: disable=W5101

import uuid

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.utils import IntegrityError

from base.models import EntityMixin
from core.model import track_data
from gatheros_subscription.models import Lot, Subscription


@track_data('status', 'boleto_url', )
class Transaction(models.Model, EntityMixin):
    PROCESSING = 'processing'
    AUTHORIZED = 'authorized'
    PAID = 'paid'
    WAITING_PAYMENT = 'waiting_payment'
    REFUNDED = 'refunded'
    PENDING_REFUND = 'pending_refund'
    REFUSED = 'refused'
    CHARGEDBACK = 'chargedback'

    MANUAL = 'manual'
    BOLETO = 'boleto'
    CREDIT_CARD = 'credit_card'

    TRANSACTION_STATUS = (
        (PROCESSING, 'Processando'),
        (AUTHORIZED, 'Autorizado'),
        (PAID, 'Pago'),
        (WAITING_PAYMENT, 'Aguardando pagamento'),
        (REFUNDED, 'Estornado'),
        (PENDING_REFUND, 'Aguardando estorno'),
        (REFUSED, 'Recusada'),
        (CHARGEDBACK, 'Chargeback')
    )

    TRANSACTION_TYPES = (
        (BOLETO, 'Boleto'),
        (CREDIT_CARD, 'Cartão de credito'),
        (MANUAL, 'Manual'),
    )

    MANUAL_PAYMENT_MONEY = 'money'
    MANUAL_PAYMENT_PAYCHECK = 'paycheck'
    MANUAL_PAYMENT_DEBIT_CARD = 'debit_card'
    MANUAL_PAYMENT_CREDIT_CARD = 'credit_card'
    MANUAL_PAYMENT_BANK_DEPOSIT = 'bank_deposit'
    MANUAL_PAYMENT_BANK_TRANSFER = 'bank_transfer'
    MANUAL_WAITING_PAYMENT = 'waiting_payment'

    MANUAL_PAYMENT_TYPES = (
        (MANUAL_PAYMENT_MONEY, 'Dinheiro'),
        (MANUAL_PAYMENT_PAYCHECK, 'Cheque'),
        (MANUAL_PAYMENT_DEBIT_CARD, 'Cartão de Débito'),
        (MANUAL_PAYMENT_CREDIT_CARD, 'Cartão de Crédito'),
        (MANUAL_PAYMENT_BANK_DEPOSIT, 'Depósito'),
        (MANUAL_PAYMENT_BANK_TRANSFER, 'Transferência bancária'),
        # (MANUAL_WAITING_PAYMENT, 'Aguardando pagamento'),
    )

    class Meta:
        verbose_name = 'Transação'
        verbose_name_plural = 'Transações'

    def __str__(self):
        return self.subscription.person.name + ' - ' + self.subscription.event.name

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        primary_key=True
    )

    status = models.CharField(
        max_length=30,
        choices=TRANSACTION_STATUS,
        null=True,
        blank=True,
    )

    type = models.CharField(
        max_length=30,
        choices=TRANSACTION_TYPES,
        null=True,
        blank=True,
    )

    date_created = models.DateTimeField(
        max_length=30,
        null=True,
        blank=True,
    )

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.DO_NOTHING,
        related_name='transactions'
    )

    lot = models.ForeignKey(
        Lot,
        on_delete=models.DO_NOTHING,
        related_name='transactions',
        editable=False,
        null=True,
        blank=True,
    )

    part = models.ForeignKey(
        'installment.Part',
        on_delete=models.DO_NOTHING,
        verbose_name='transação da parcela',
        related_name='transactions',
        # Not required
        blank=True,
        null=True,
    )

    lot_price = models.DecimalField(
        decimal_places=2,
        max_digits=11,
        null=True,
        blank=True,
    )

    installments = models.PositiveIntegerField(
        default=1,
        verbose_name='parcelas',
        blank=True,
        null=True,
    )

    installment_part = models.PositiveIntegerField(
        default=1,
        verbose_name='número de parcelas',
        blank=True,
        null=True,
    )

    installment_amount = models.DecimalField(
        decimal_places=2,
        max_digits=11,
        verbose_name='valor da parcelas',
        blank=True,
        null=True,
    )

    amount = models.DecimalField(
        decimal_places=2,
        max_digits=11,
        null=True,
        blank=True,
        verbose_name='valor do pagamento',
    )

    liquid_amount = models.DecimalField(
        decimal_places=2,
        max_digits=11,
        null=True,
        blank=True,
    )

    boleto_url = models.TextField(
        verbose_name='URL do boleto',
        null=True,
        blank=True,
    )

    boleto_expiration_date = models.DateField(
        verbose_name='vencimento do boleto',
        null=True,
        blank=True,
    )

    credit_card_holder = models.CharField(
        max_length=80,
        null=True,
        blank=True,
    )

    credit_card_first_digits = models.CharField(
        max_length=6,
        null=True,
        blank=True,
    )

    credit_card_last_digits = models.CharField(
        max_length=4,
        null=True,
        blank=True,
    )

    manual = models.BooleanField(
        default=False,
        verbose_name='lançado manualmente',
    )

    manual_payment_type = models.CharField(
        max_length=30,
        choices=MANUAL_PAYMENT_TYPES,
        null=True,
        blank=True,
        verbose_name='tipo de recebimento manual',
    )

    manual_author = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='author do pagamento manual',
    )

    data = JSONField(
        null=True,
        blank=True,
    )

    pagarme_id = models.PositiveIntegerField(
        null=True,
        editable=False,
        verbose_name='ID da transação (pagar.me)',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._transaction_liquid_amount = None

    def save(self, *args, **kwargs):
        if self._state.adding is True:
            self.lot = self.subscription.lot

        elif self.lot.event != self.subscription.event:
            raise IntegrityError(
                'O lote informado na edição não pertence à inscrição da'
                ' transação.'
            )

        return super().save(*args, **kwargs)

    @property
    def paid(self):
        return self.status == self.PAID

    @property
    def pending(self):
        return \
            self.status == self.WAITING_PAYMENT \
            or self.status == self.PROCESSING \
            or self.status == self.AUTHORIZED

    @property
    def cancelled(self):
        return \
            self.status == self.REFUNDED \
            or self.status == self.PENDING_REFUND \
            or self.status == self.REFUSED \
            or self.status == self.CHARGEDBACK

    @property
    def transaction_amount(self):
        """
        O valor total pago pelo participante
        :return: DecimalField
        """
        # return self.amount + self.optional_amount
        return self.amount

    @property
    def transaction_liquid_amount(self):
        """
        O valor total que o organizador irá receber
        :return: DecimalField
        """
        if self._transaction_liquid_amount:
            return self._transaction_liquid_amount

        liquid_amount = self.liquid_amount

        split_rules = self.split_rules.filter(
            is_congressy=False,
            recipient_id=self.lot.event.organization.recipient_id,
        )
        if split_rules.count():
            split_rule = split_rules[0]

            payables = split_rule.payables.filter(type='credit')

            if payables.count():
                amount = sum([p.amount for p in payables])
                fee = sum([p.antecipation_fee for p in payables])
                liquid_amount = amount - fee if fee else amount
            else:
                liquid_amount = split_rule.amount

        self._transaction_liquid_amount = round(liquid_amount, 2)

        # return self.liquid_amount + self.optional_liquid_amount
        return self._transaction_liquid_amount

# class Transaction(models.Model):
#     class Meta:
#         verbose_name = 'Transação'
#         verbose_name_plural = 'Transações'
#
#     PROCESSING = 'processing'
#     AUTHORIZED = 'authorized'
#     PAID = 'paid'
#     WAITING_PAYMENT = 'waiting_payment'
#     REFUNDED = 'refunded'
#     PENDING_REFUND = 'pending_refund'
#     REFUSED = 'refused'
#     CHARGEDBACK = 'chargedback'
#
#     BOLETO = 'boleto'
#     CREDIT_CARD = 'credit_card'
#
#     TRANSACTION_STATUS = (
#         (PROCESSING, 'Processando'),
#         (AUTHORIZED, 'Autorizado'),
#         (PAID, 'Pago'),
#         (WAITING_PAYMENT, 'Aguardando pagamento'),
#         (REFUNDED, 'Estornado'),
#         (PENDING_REFUND, 'Aguardando estorno'),
#         (REFUSED, 'Recusada'),
#         (CHARGEDBACK, 'Chargeback')
#     )
#
#     TRANSACTION_TYPES = (
#         (BOLETO, 'Boleto'),
#         (CREDIT_CARD, 'Cartão de credito'),
#     )
#
#     uuid = models.UUIDField(
#         default=uuid.uuid4,
#         editable=False,
#         unique=True,
#         primary_key=True
#     )
#
#     provider = models.OneToOneField(
#         Provider,
#         on_delete=models.CASCADE,
#         verbose_name='provedor',
#         related_name='transaction',
#         null=True, # REMOVER
#         blank=True,# REMOVER
#     )
#
#     status = models.CharField(
#         max_length=30,
#         choices=TRANSACTION_STATUS,
#         null=True,
#         blank=True,
#     )
#
#     type = models.CharField(
#         max_length=30,
#         choices=TRANSACTION_TYPES,
#         null=True,
#         blank=True,
#     )
#
#     date_created = models.DateTimeField(
#         max_length=30,
#         null=True,
#         blank=True,
#     )
#
#     amount = models.DecimalField(
#         decimal_places=2,
#         max_digits=11,
#         null=True,
#         blank=True,
#         verbose_name='valor do pagamento',
#     )
#
#     installments = models.PositiveIntegerField(
#         default=1,
#         verbose_name='parcelas',
#         blank=True,
#         null=True,
#     )
#
#     boleto_url = models.TextField(
#         verbose_name='URL do boleto',
#         null=True,
#         blank=True,
#     )
#
#     boleto_expiration_date = models.DateField(
#         verbose_name='vencimento do boleto',
#         null=True,
#         blank=True,
#     )
#
#     card_holder = models.CharField(
#         max_length=80,
#         null=True,
#         blank=True,
#     )
#
#     card_first_digits = models.CharField(
#         max_length=6,
#         null=True,
#         blank=True,
#     )
#
#     card_last_digits = models.CharField(
#         max_length=4,
#         null=True,
#         blank=True,
#     )
#
#     data = JSONField(
#         null=True,
#         blank=True,
#     )
#
#     @property
#     def paid(self):
#         return self.status == self.PAID
#
#     @property
#     def pending(self):
#         return \
#             self.status == self.WAITING_PAYMENT \
#             or self.status == self.PROCESSING \
#             or self.status == self.AUTHORIZED
#
#     @property
#     def cancelled(self):
#         return \
#             self.status == self.REFUNDED \
#             or self.status == self.PENDING_REFUND \
#             or self.status == self.REFUSED \
#             or self.status == self.CHARGEDBACK
#
#     def __str__(self):
#         return '{} - {}'.format(
#             self.subscription.person.name,
#             self.subscription.event.name,
#         )
#
#     def save(self, *args, **kwargs):
#         if self._state.adding is True:
#             self.lot = self.subscription.lot
#
#         return super().save(*args, **kwargs)
