# pylint: disable=W5101

import uuid

from django.contrib.postgres.fields import JSONField
from django.db import models

from .transaction import Transaction


class TransactionStatus(models.Model):
    PROCESSING = 'processing'
    AUTHORIZED = 'authorized'
    PAID = 'paid'
    WAITING_PAYMENT = 'waiting_payment'
    REFUNDED = 'refunded'
    PENDING_REFUND = 'pending_refund'
    REFUSED = 'refused'
    CHARGEDBACK = 'chargedback'

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

    class Meta:
        verbose_name = 'Status de Transação'
        verbose_name_plural = 'Status de Transações'
        ordering = ['date_created']

    def __str__(self):
        return self.transaction.subscription.person.name + ' - ' \
               + self.transaction.subscription.event.name + ' -- ' \
               + self.transaction.type

    status = models.CharField(
        max_length=30,
        choices=TRANSACTION_STATUS,
        null=True,
        blank=True,
    )

    date_created = models.CharField(
        max_length=30,
        null=True,
        blank=True,
    )

    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name='statuses'
    )

    data = JSONField()
