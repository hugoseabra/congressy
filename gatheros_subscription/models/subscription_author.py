from django.db import models

from gatheros_subscription.models import Subscription
from survey.models import Author


class SubscriptionAuthor(models.Model):
    """Modelo de formularios de evento"""

    subscription = models.OneToOneField(
        Subscription,
        on_delete=models.CASCADE,
        verbose_name='inscrição',
        related_name='subscription_author'
    )

    author = models.OneToOneField(
        Author,
        on_delete=models.CASCADE,
        verbose_name='autor',
        related_name='subscription',
    )

    def __str__(self):
        return self.author.name
