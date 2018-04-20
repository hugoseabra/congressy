"""
    Representação do serviços de opcional(add ons)
"""

from django.db import models

from .optional_interface import OptionalInterface
from .theme import Theme


class OptionalService(models.Model, OptionalInterface):
    start_on = models.DateTimeField()

    duration = models.PositiveIntegerField()

    theme = models.ForeignKey(
        Theme,
        on_delete=models.PROTECT,

    )
