"""
    Representação dos opcionais(add ons) de inscrições(subscriptions)
"""

from django.db import models

from .optional_service import OptionalService
from .subscription_optional_interface import SubscriptionOptionalInterface


class SubscriptionOptional(models.Model, SubscriptionOptionalInterface):
    optional_service = models.ForeignKey(
        OptionalService,
        on_delete=models.CASCADE,
        verbose_name='opcional de produto',
        related_name='products'
    )
