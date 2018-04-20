"""
    Representação do serviços de opcional(add ons)
"""

from django.db import models

from gatheros_subscription.models import LotCategory
from .optional_interface import OptionalInterface
from .theme import Theme


class OptionalService(OptionalInterface):
    datetime_start = models.DateTimeField()

    duration = models.PositiveIntegerField()

    published = models.BooleanField()

    has_cost = models.BooleanField()

    lot_categories = models.ManyToManyField(LotCategory)

    theme = models.ForeignKey(
        Theme,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )
