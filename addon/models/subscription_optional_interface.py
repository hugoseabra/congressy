"""
    Representação da interface de opcionais(add ons) de inscrições(
    subscriptions)
"""

from django.db import models

from gatheros_subscription.models import Subscription


class SubscriptionOptionalInterface(object):

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='optionals',
        verbose_name='inscrição'
    )
    created = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField()

    count = models.PositiveIntegerField()
    total_allowed = models.PositiveIntegerField()
