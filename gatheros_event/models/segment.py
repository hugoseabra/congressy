# pylint: disable=W5101
"""
Segmentos são importantes para cruzar os segmentos atendidos por um evento e,
por sua vez, saber quais os segmentos de interesses das pessoas participantes
de eventos.
"""

from django.db import models


class Segment(models.Model):
    """ Modelo para as 'Cadeias Produtivas' """

    name = models.CharField(max_length=255, verbose_name='nome')
    active = models.BooleanField(default=True, verbose_name='ativo')
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='descrição'
    )

    class Meta:
        verbose_name = 'Cadeia Produtiva'
        verbose_name_plural = 'Cadeias Produtivas'
        ordering = ['name']

    def __str__(self):
        return self.name
