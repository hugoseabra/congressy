"""
    Representação da interface de opcionais(add ons)
"""

from django.db import models
from gatheros_subscription.models import LotCategory
from .optional_type import OptionalType


class OptionalInterface(models.Model):

    subscription_datetime = models.DateTimeField()

    description = models.TextField()

    quantity = models.PositiveIntegerField()

    published = models.BooleanField()

    has_cost = models.BooleanField()

    lot_categories = models.ManyToManyField(LotCategory)

    optional_type = models.ForeignKey(
        OptionalType,
        on_delete=models.DO_NOTHING,
    )
