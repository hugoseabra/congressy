"""
    Representação da interface de opcionais(add ons) de inscrições(
    subscriptions)
"""

from django.db import models

from gatheros_subscription.models import Subscription


class SubscriptionOptionalInterface(models.Model):

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
    )
    created = models.DateTimeField()
    price = models.TextField()

    count = models.PositiveIntegerField()
    total_allowed = models.PositiveIntegerField()
