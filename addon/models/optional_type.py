# pylint: disable=W5101

"""
    Representação dos tipo dos opcionais(add ons)
"""

from django.db import models

from base.models import EntityMixin


class OptionalServiceType(EntityMixin, models.Model):
    """
        Tipo de opcional: palestra, workshop, dentre outros.
    """
    class Meta:
        verbose_name = 'tipo de opcional de serviço'
        verbose_name_plural = 'tipos de opcional de serviço'
        ordering = ('name',)

    name = models.CharField(max_length=255, verbose_name='nome')

    def __str__(self):
        return self.name


class OptionalProductType(EntityMixin, models.Model):
    """
        Tipo de opcional: caneca, camiseta, etc.
    """
    class Meta:
        verbose_name = 'tipo de opcional de produto'
        verbose_name_plural = 'tipos de opcional de produto'
        ordering = ('name',)

    name = models.CharField(max_length=255, verbose_name='nome')

    def __str__(self):
        return self.name
