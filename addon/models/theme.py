"""
    Representação dos temas dos opcionais(add ons)
"""

from django.db import models

from base.models import EntityMixin


class Theme(EntityMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name='nome')
    limit = models.PositiveIntegerField(
        verbose_name='limitar quantidade',
        null=True,
        blank=True,
        help_text='Limitar número de inscrições de um mesmo participante em um'
                  ' mesmo tema.',
    )
