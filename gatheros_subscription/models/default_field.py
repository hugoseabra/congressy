# pylint: disable=W5101
"""
Campo padrão de formulário, que deve conter nos formulários de todos os
eventos da plataforma.
"""

from . import AbstractField


class DefaultField(AbstractField):
    """ Modelo de camp padrão. """

    class Meta:
        verbose_name = 'Campo Padrão'
        verbose_name_plural = 'Campos Padrão'
        ordering = ['order']

    def __str__(self):
        return self.label
