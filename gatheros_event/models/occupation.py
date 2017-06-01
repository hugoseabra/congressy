# pylint: disable=W5101
"""
Ocupação de pessoas.
"""

from django.db import models


class Occupation(models.Model):
    """ Profissão """
    name = models.CharField(max_length=100, unique=True, verbose_name='nome')
    active = models.BooleanField(default=True, verbose_name='ativo')

    class Meta:
        verbose_name = 'Profissão'
        verbose_name_plural = 'Profissões'
        ordering = ['name']

    def __str__(self):
        return self.name
