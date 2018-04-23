"""
    Representação da interface de opcionais(add ons) de inscrições(
    subscriptions)
"""

from django.db import models

from base.models import EntityMixin
from gatheros_subscription.models import Subscription


class AbstractSubscriptionOptional(EntityMixin, models.Model):
    class Meta:
        abstract = True

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='%(class)s_optionals',
        verbose_name='inscrição',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="data de criação",
    )
    price = models.DecimalField(
        verbose_name='preço',
        decimal_places=2,
        max_digits=10,
    )

    count = models.PositiveIntegerField(
        verbose_name="quantidade até agora",
        default=0,
        blank=True,
    )
    total_allowed = models.PositiveIntegerField(
        verbose_name="total permitido",
    )
