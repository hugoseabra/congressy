# pylint: disable=W5101
"""
Campo padrão de formulário, que deve conter nos formulários de todos os
eventos da plataforma.
"""

from django.db import models
from core.util import model_field_slugify

from . import AbstractField


class DefaultField(AbstractField):
    """ Modelo de camp padrão. """

    order = models.PositiveIntegerField(
        verbose_name='ordem',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Campo Padrão'
        verbose_name_plural = 'Campos Padrão'
        ordering = ['order']

    def __str__(self):
        return self.label

    def save(self, **kwargs):
        self.name = model_field_slugify(
            model_class=self.__class__,
            instance=self,
            string=self.label if not self.name else self.name,
            slug_field='name'
        )

        super(DefaultField, self).save(**kwargs)
