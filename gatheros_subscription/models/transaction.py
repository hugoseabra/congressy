# pylint: disable=W5101
"""
Inscrições de pessoas em eventos conforme registrado no pagarme.
"""

from django.db import models


class Transaction(models.Model):

    id = models.IntegerField(
        primary_key=True,
        unique=True,
    )




