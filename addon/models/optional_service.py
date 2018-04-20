"""
    Representação do serviços de opcional(add ons)
"""

from django.db import models

from .optional_interface import OptionalInterface
from .theme import Theme


class OptionalService(models.Model, OptionalInterface):
    start_on = models.DateTimeField(
        verbose_name="data de inicio",
    )

    duration = models.PositiveIntegerField(
        verbose_name="duração",
    )

    theme = models.ForeignKey(
        Theme,
        on_delete=models.PROTECT,
        verbose_name="themas",
        related_name="services",
    )
