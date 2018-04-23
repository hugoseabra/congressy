# pylint: disable=W5101

"""
    Representação dos preços dos opcionais(add ons)
"""

from django.db import models

from base.models import EntityMixin
from gatheros_subscription.models import LotCategory
from .optional import OptionalProduct, OptionalService


class AbstractPrice(EntityMixin, models.Model):
    """
        Opcionais pagos possuem preços que passar a assumi
    """
    class Meta:
        abstract = True

    lot_category = models.ForeignKey(
        LotCategory,
        on_delete=models.DO_NOTHING,
        related_name='%(class)s_prices',
    )

    date_start = models.DateTimeField(verbose_name='data inicial')
    date_end = models.DateTimeField(verbose_name='data final')

    price = models.DecimalField(
        verbose_name='preço',
        decimal_places=2,
        max_digits=10,
    )


class ProductPrice(AbstractPrice):
    optional_product = models.ForeignKey(
        OptionalProduct,
        on_delete=models.CASCADE,
        related_name='prices',
    )


class ServicePrice(AbstractPrice):
    optional_service = models.ForeignKey(
        OptionalService,
        on_delete=models.CASCADE,
        related_name='prices',
    )
