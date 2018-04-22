"""
    Representação da interface de opcionais(add ons)
"""

from django.db import models

from base.models import EntityMixin
from gatheros_subscription.models import LotCategory
from .optional_type import OptionalType


class OptionalInterface(EntityMixin, models.Model):
    class Meta:
        abstract = True

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
        related_name='%(class)s_optionals'
    )

    optional_type = models.ForeignKey(
        OptionalType,
        on_delete=models.PROTECT,
        verbose_name='tipo',
        related_name='%(class)s_optionals',
    )

    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="criado",
    )

    modified = models.DateTimeField(
        auto_now=True,
        verbose_name="modificado",
        null=True,
        editable=False,
    )

    created_by = models.CharField(
        null=True,
        editable=False,
        max_length=255,
        verbose_name="criado por",
    )

    modified_by = models.CharField(
        null=True,
        max_length=255,
        verbose_name="modificado por",
    )
