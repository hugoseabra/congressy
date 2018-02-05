# pylint: disable=W5101

import uuid

from django.contrib.postgres.fields import JSONField
from django.db import models

from .transaction import Transaction


class TransactionStatus(models.Model):

    class Meta:
        verbose_name = 'Status de Transação'
        verbose_name_plural = 'Status de Transações'


    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        primary_key=True
    )

    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE
    )

    data = JSONField()
