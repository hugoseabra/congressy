"""
    Survey domain model.
"""
from django.db import models


class Survey(models.Model):
    """
        Survey domain model implementation.
    """

    class Meta:
        verbose_name = 'questionario'
        verbose_name_plural = 'questionarios'

    name = models.CharField(
        max_length=255,
        verbose_name='nome',
        help_text='Nome do questionario'
    )