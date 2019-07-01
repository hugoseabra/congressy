"""
    Representação dos temas dos opcionais(add ons)
"""

from django.db import models

from base.models import EntityMixin
from core.model import track_data
from gatheros_event.models import Event
from gatheros_event.models.mixins import GatherosModelMixin


@track_data('name', 'limit')
class Theme(GatherosModelMixin, EntityMixin, models.Model):

    class Meta:
        verbose_name_plural = 'grupos'
        verbose_name = 'grupo'
        ordering = ('event', 'name')

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name="eventos",
        related_name="themes",
    )

    name = models.CharField(max_length=255, verbose_name='nome')
    limit = models.PositiveIntegerField(
        verbose_name='limitar quantidade',
        null=True,
        blank=True,
        help_text='Limitar número de inscrições de um mesmo participante em um'
                  ' mesmo tema.',
    )

    def __str__(self):
        string = self.name
        if self.limit and self.limit > 0:
            string += ' (limitado)'

        return string
