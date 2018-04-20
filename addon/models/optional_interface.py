"""
    Representação da interface de opcionais(add ons)
"""

from django.contrib.auth.models import User
from django.db import models

from gatheros_subscription.models import LotCategory
from .optional_type import OptionalType


class OptionalInterface(object):
    date_end = models.DateTimeField(
        verbose_name="data final",
    )

    description = models.TextField(
        verbose_name="descrição",
    )

    quantity = models.PositiveIntegerField(
        verbose_name="quantidade",
    )

    published = models.BooleanField(
        verbose_name="publicado",
    )

    has_cost = models.BooleanField(
        verbose_name="possui custo",
    )

    lot_categories = models.ManyToManyField(
        LotCategory,
        verbose_name='categorias',
        related_name='optionals'
    )

    optional_type = models.ForeignKey(
        OptionalType,
        on_delete=models.PROTECT,
        verbose_name='tipo',
        related_name='optionals',
    )

    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="criado",
    )

    modified = models.DateTimeField(
        auto_now=True,
        verbose_name="modificado",
    )

    created_by = models.ForeignKey(
        User,
        null=True,
        editable=False,
        verbose_name="criado por",
    )
    modified_by = models.ForeignKey(
        User,
        null=True,
        editable=False,
        verbose_name="modificado por",
    )
