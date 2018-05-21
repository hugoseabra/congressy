"""
    Author domain model.
"""
from django.contrib.auth.models import User
from django.db import models

from .work import Work
from base.models import Entity


class Author(Entity, models.Model):
    """
        Author domain model implementation.
    """

    class Meta:
        verbose_name = 'autor'
        verbose_name_plural = 'autores'

    def __str__(self):  # pragma: no cover
        return self.name

    work = models.ForeignKey(
        Work,
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
        related_name='work_authors',
    )

    name = models.CharField(
        max_length=255,
        verbose_name='nome',
    )

    created = models.DateTimeField(
        auto_now=True,
        verbose_name='criado em'
    )
