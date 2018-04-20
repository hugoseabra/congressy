"""
    Representação dos opcionais(add ons) de serviço de  inscrições(
    subscriptions)
"""

from django.db import models

from .optional import Optional
from .subscription_optional_interface import SubscriptionOptionalInterface


class SubscriptionOptionalService(models.Model, SubscriptionOptionalInterface):
    optional = models.ForeignKey(
        Optional,
        on_delete=models.DO_NOTHING,
        verbose_name='opcional de serviço',
        related_name='services'
    )
