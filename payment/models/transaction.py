# pylint: disable=W5101

import uuid

from django.contrib.postgres.fields import JSONField
from django.db import models

from gatheros_subscription.models import Subscription


class Transaction(models.Model):

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
        (CREDIT_CARD, 'Cartão de credito')
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

    date_created = models.CharField(
        max_length=30,
        null=True,
        blank=True,
    )

    amount = models.IntegerField(
        null=True,
        blank=True,
    )

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.DO_NOTHING,
        related_name='transactions'
    )

    data = JSONField()
