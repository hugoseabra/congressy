# pylint: disable=W5101
"""
Associado de uma organização.
"""
from django.db import models

from base.models import EntityMixin
from gatheros_event.models import Organization


class Associate(EntityMixin, models.Model):
    """ Associado de Organzação. """

    name = models.CharField(max_length=255, verbose_name='nome')
    active = models.BooleanField(default=True, verbose_name='ativo')

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        verbose_name='organização',
        related_name='associates'
    )

    class Meta:
        verbose_name = 'Associado'
        verbose_name_plural = 'Associados'
        ordering = ['name']

    def __str__(self):
        return self.name
