# pylint: disable=W5101
import uuid
from decimal import Decimal

from django.db import models

from base.models import EntityMixin
from core.model import track_data

"""
{
    "object": "split_rule",
    "id": "sr_cjyg3wf3100y6dh6ddm9pzsvx",
    "liable": true,
    "amount": 1700,
    "percentage": null,
    "recipient_id": "re_cjcupb1iq0200zl6d89r92s32",
    "charge_remainder": true,
    "charge_processing_fee": true,
    "block_id": null,
    "date_created": "2019-07-23T17:42:07.453Z",
    "date_updated": "2019-07-23T17:42:07.453Z"
},
"""


@track_data('pagarme_id')
class SplitRule(models.Model, EntityMixin):
    class Meta:
        verbose_name = 'Regra de Rateamento'
        verbose_name_plural = 'Regras de rateamento'

    def __str__(self):
        return 'ID: {} ({}), Transaction: {}'.format(
            self.pk,
            self.pagarme_id,
            self.transaction_id,
        )

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        primary_key=True
    )

    transaction = models.ForeignKey(
        'payment.Transaction',
        on_delete=models.CASCADE,
        related_name='split_rules',
        null=False,
        editable=False,
        verbose_name='transação',
    )

    pagarme_id = models.CharField(
        max_length=28,
        null=False,
        editable=False,
        verbose_name='ID de regra (pagar.me)',
    )

    is_congressy = models.BooleanField(
        null=False,
        verbose_name='se congressy',
    )

    charge_processing_fee = models.BooleanField(
        default=False,
        null=False,
        verbose_name='responsável pelas taxas'
    )

    amount = models.DecimalField(
        default=Decimal(0.00),
        verbose_name='montante',
        decimal_places=10,
        max_digits=25,
        null=False,
    )

    recipient_id = models.CharField(
        max_length=28,
        null=False,
        editable=False,
        verbose_name='ID recebedor (pagar.me)',
    )

    created = models.DateTimeField(
        editable=False,
        null=False,
        verbose_name='criado em',
    )
