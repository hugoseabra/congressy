# pylint: disable=W5101

"""
    Representação dos opcionais(add ons) de inscrições(subscriptions)
"""

from django.db import models

from base.models import EntityMixin
from .optional_product import OptionalProduct
from .base_subscription_optional import AbstractSubscriptionOptional


class SubscriptionOptionalProduct(AbstractSubscriptionOptional):
    optional_product = models.ForeignKey(
        OptionalProduct,
        on_delete=models.CASCADE,
        verbose_name='opcional de produto',
        related_name='products'
    )
