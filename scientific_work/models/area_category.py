from django.db import models
from gatheros_event.models import Event


class AreaCategory(models.Model):

    class Meta:
        verbose_name = 'Categoria de Área'
        verbose_name_plural = 'Categorias de Àreas'

    name = models.CharField(
        max_length=80,
        verbose_name="área temática",
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="area_categories",
    )

    def __str__(self):
        return self.name
