"""
    Representação dos opcionais(add ons) de inscrições(subscriptions)
"""

from django.db import models

from .optional_product import OptionalProduct
from .subscription_optional_interface import SubscriptionOptionalInterface


class SubscriptionOptionalProduct(models.Model, SubscriptionOptionalInterface):

    optional_product = models.ForeignKey(
        OptionalProduct,
        on_delete=models.CASCADE,
        verbose_name='opcional de produto',
        related_name='products'
    )
