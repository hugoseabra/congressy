# pylint: disable=W5101

"""
    Representação do opcional(add ons)
"""

from django.db import models

from base.models import EntityMixin
from .optional_interface import OptionalInterface


class OptionalProduct(EntityMixin, models.Model, OptionalInterface):
    pass
