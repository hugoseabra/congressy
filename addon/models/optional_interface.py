"""
    Representação da interface de opcionais(add ons)
"""

from django.contrib.auth.models import User
from django.db import models

from gatheros_subscription.models import LotCategory
from .optional_type import OptionalType


class OptionalInterface(object):
    date_end = models.DateTimeField()

    description = models.TextField()

    quantity = models.PositiveIntegerField()

    published = models.BooleanField()

    has_cost = models.BooleanField()

    lot_categories = models.ManyToManyField(
        LotCategory,
        verbose_name='categorias',
        related_name='optionals'
    )

    optional_type = models.ForeignKey(
        OptionalType,
        on_delete=models.PROTECT,
        verbose_name='tipo',
        related_name='optionals'
    )

    created = models.DateTimeField(
        auto_now_add=True
    )

    modified = models.DateTimeField(
        auto_now=True
    )

    created_by = models.ForeignKey(User, null=True, editable=False)
    modified_by = models.ForeignKey(User, null=True, editable=False)
