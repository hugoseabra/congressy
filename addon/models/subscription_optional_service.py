# pylint: disable=W5101

"""
    Representação dos opcionais(add ons) de serviço de  inscrições(
    subscriptions)
"""

from django.db import models

from base.models import EntityMixin
from .optional_service import OptionalService
from .subscription_optional_interface import SubscriptionOptionalInterface


class SubscriptionOptionalService(EntityMixin, models.Model,
                                  SubscriptionOptionalInterface):
    optional = models.ForeignKey(
        OptionalService,
        on_delete=models.DO_NOTHING,
        verbose_name='opcional de serviço',
        related_name='services'
    )
