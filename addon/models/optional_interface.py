"""
    Representação da interface de opcionais(add ons)
"""

from django.contrib.auth.models import User
from django.db import models

from gatheros_subscription.models import LotCategory
from .optional_type import OptionalType
from .price import Price

class OptionalInterface(models.Model):
    date_end = models.DateTimeField()

    description = models.TextField()

    quantity = models.PositiveIntegerField()

    published = models.BooleanField()

    has_cost = models.BooleanField()

    lot_categories = models.ManyToManyField(LotCategory)

    optional_type = models.ForeignKey(
        OptionalType,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )

    price = models.ForeignKey(
        Price,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )

    datetime_created = models.DateTimeField(
        auto_now_add=True
    )

    datetime_modified = models.DateTimeField(
        auto_now=True
    )

    created_by = models.ForeignKey(User, null=True, editable=False)
    modified_by = models.ForeignKey(User, null=True, editable=False)
