"""
    Representação dos opcionais(add ons) de inscrições(subscriptions)
"""

from django.db import models

from .optional_service import OptionalService
from .subscription_optional_interface import SubscriptionOptionalInterface


class SubscriptionOptional(SubscriptionOptionalInterface):
    optional_service = models.ForeignKey(
        OptionalService,
        on_delete=models.DO_NOTHING,
    )
