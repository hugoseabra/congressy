"""
    Representação dos tipo dos opcionais(add ons)
"""

from django.db import models


class OptionalType(models.Model):

    name = models.CharField(max_length=255, verbose_name='nome')
