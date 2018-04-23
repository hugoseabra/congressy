# pylint: disable=W5101

"""
    Representação do opcional(add ons)
"""

from .base_optional import AbstractOptional


class OptionalProduct(AbstractOptional):

    def __str__(self):
        return self.description
