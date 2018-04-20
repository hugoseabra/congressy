"""
    Representação do opcional(add ons)
"""

from django.db import models

from .optional_interface import OptionalInterface


class OptionalProduct(models.Model, OptionalInterface):
    pass
