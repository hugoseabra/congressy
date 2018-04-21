"""
    Representação dos temas dos opcionais(add ons)
"""

from django.db import models
from base.models import EntityMixin

class Theme(EntityMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name='nome')
