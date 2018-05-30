from django.db import models
from gatheros_event.models import Event


class AreaCategory(models.Model):

    name = models.CharField(
        max_length=25,
        verbose_name="área temática",
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="area_categories",
    )

    def __str__(self):
        return self.name