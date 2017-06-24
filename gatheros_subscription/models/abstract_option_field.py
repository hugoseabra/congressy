# pylint: disable=W5101
"""
Opção de campo Padrão vinculada a um Campo Padrão de formulário.
"""

from django.db import models

from gatheros_event.models.mixins import GatherosModelMixin


class AbstractDefaultFieldOption(models.Model, GatherosModelMixin):
    """ Modelo de opção de campo. """

    name = models.CharField(max_length=255, verbose_name='rótulo')
    value = models.CharField(
        max_length=255,
        verbose_name='valor',
        null=True,
        blank=True
    )

    class Meta:
        abstract = True
