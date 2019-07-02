"""
    Survey domain model.
    Questionário para acumular perguntas diversas de um determinado autor.
"""
from django.db import models

from core.model import track_data
from survey.models.mixins import Entity


@track_data('name')
class Survey(Entity, models.Model):
    """
        Survey domain model implementation.
    """

    class Meta:
        verbose_name = 'questionario'
        verbose_name_plural = 'questionarios'

    def __str__(self):  # pragma: no cover
        return self.name

    name = models.CharField(
        max_length=255,
        verbose_name='nome',
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='descrição'
    )

    created = models.DateTimeField(
        verbose_name='criado em',
        auto_now_add=True,
    )
