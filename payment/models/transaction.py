# pylint: disable=W5101

import uuid

from django.contrib.postgres.fields import JSONField
from django.db import models

from gatheros_subscription.models import Subscription


class Transaction(models.Model):

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        primary_key=True
    )

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.DO_NOTHING
    )

    data = JSONField()
