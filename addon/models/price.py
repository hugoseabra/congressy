"""
    Representação dos preços dos opcionais(add ons)
"""

from django.db import models
from gatheros_subscription.models import LotCategory


class Price(models.Model):

    lot_category = models.ForeignKey(
        LotCategory,
        on_delete=models.DO_NOTHING,
        related_name='prices',
        null=True,
        blank=True,
    )

    price = models.DecimalField(
        verbose_name='preço',
        decimal_places=2,
        max_digits=10,
    )

    release_days = models.PositiveIntegerField(
        verbose_name=''
    )