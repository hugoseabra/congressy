# pylint: disable=W5101

"""
    Representação dos opcionais(add ons) de serviço de  inscrições(
    subscriptions)
"""

from django.db import models

from .optional_service import OptionalService
from .base_subscription_optional import AbstractSubscriptionOptional


class SubscriptionOptionalService(AbstractSubscriptionOptional):
    optional_service = models.ForeignKey(
        OptionalService,
        on_delete=models.DO_NOTHING,
        verbose_name='opcional de serviço',
        related_name='services'
    )
