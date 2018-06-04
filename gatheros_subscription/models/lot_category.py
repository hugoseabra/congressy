# pylint: disable=W5101
"""
Categoria de lote são importantes para agrupar os lotes em estruturas
que se assemelham e ajudar a estruturar a apresentação do lote para
o organizador, além de centralizar diversas características do evento.
"""
from django.db import models
from gatheros_event.models.mixins import GatherosModelMixin
from gatheros_event.models import Event


class LotCategory(models.Model, GatherosModelMixin):
    """ Categoria de lote """

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name='evento',
        related_name='lot_categories'
    )

    name = models.CharField(max_length=50, verbose_name='nome')
    active = models.BooleanField(default=True, verbose_name='ativo')
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='descrição'
    )

    class Meta:
        verbose_name = 'Categoria de Lote'
        verbose_name_plural = 'Categorias de Lote'
        ordering = ['name']

    def __str__(self):
        return self.name
