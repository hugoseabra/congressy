# pylint: disable=W5101

import uuid

from django.contrib.postgres.fields import JSONField
from django.db import models

from .provider import Provider


class Transaction(models.Model):
    class Meta:
        verbose_name = 'Transação'
        verbose_name_plural = 'Transações'

    PROCESSING = 'processing'
    AUTHORIZED = 'authorized'
    PAID = 'paid'
    WAITING_PAYMENT = 'waiting_payment'
    REFUNDED = 'refunded'
    PENDING_REFUND = 'pending_refund'
    REFUSED = 'refused'
    CHARGEDBACK = 'chargedback'

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
    )

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        primary_key=True
    )

    provider = models.OneToOneField(
        Provider,
        on_delete=models.CASCADE,
        verbose_name='provedor',
        related_name='transaction',
        null=True, # REMOVER
        blank=True,# REMOVER
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

    amount = models.DecimalField(
        decimal_places=2,
        max_digits=11,
        null=True,
        blank=True,
        verbose_name='valor do pagamento',
    )

    installments = models.PositiveIntegerField(
        default=1,
        verbose_name='parcelas',
        blank=True,
        null=True,
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

    card_holder = models.CharField(
        max_length=80,
        null=True,
        blank=True,
    )

    card_first_digits = models.CharField(
        max_length=6,
        null=True,
        blank=True,
    )

    card_last_digits = models.CharField(
        max_length=4,
        null=True,
        blank=True,
    )

    data = JSONField(
        null=True,
        blank=True,
    )

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

    def __str__(self):
        return '{} - {}'.format(
            self.subscription.person.name,
            self.subscription.event.name,
        )

    def save(self, *args, **kwargs):
        if self._state.adding is True:
            self.lot = self.subscription.lot

        return super().save(*args, **kwargs)
