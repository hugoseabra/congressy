# pylint: disable=W5101

"""
    Representação dos tipo dos opcionais(add ons)
"""

from django.db import models

from base.models import EntityMixin


class OptionalType(EntityMixin, models.Model):
    """
        Tipo de opcional: palestra, workshop, caneca, camiseta, dentre outros.
    """
    name = models.CharField(max_length=255, verbose_name='nome')

    def __str__(self):
        return self.name
