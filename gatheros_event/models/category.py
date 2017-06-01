# pylint: disable=W5101
"""
Categoria de evento são importantes para agrupar os eventos em estruturas
que se assemelham e ajudar a estruturar a apresentação do evento para
pessoas que possam se interessar em participar do evento.
"""
from django.db import models


class Category(models.Model):
    """ Categoria de evento  """

    name = models.CharField(max_length=255, verbose_name='nome')
    active = models.BooleanField(default=True, verbose_name='ativo')
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='descrição'
    )

    class Meta:
        verbose_name = 'Categoria de Evento'
        verbose_name_plural = 'Categorias de Evento'
        ordering = ['name']

    def __str__(self):
        return self.name
