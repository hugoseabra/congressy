"""
    Author domain model.
    Autor de respostas de uma questionário.
"""
from django.contrib.auth.models import User
from django.db import models

from core.model import track_data
from survey.models import Survey
from survey.models.mixins import Entity


@track_data('survey_id', 'user', 'name')
class Author(Entity, models.Model):
    """
        Author domain model implementation.
    """

    class Meta:
        verbose_name = 'autor'
        verbose_name_plural = 'autores'

    def __str__(self):  # pragma: no cover
        return self.name

    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        verbose_name='autor',
        related_name='authors',
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='usuario',
        blank=True,
        null=True,
        related_name='authors',
    )

    name = models.CharField(
        max_length=255,
        verbose_name='nome',
    )

    created = models.DateTimeField(
        auto_now=True,
        verbose_name='criado em'
    )
