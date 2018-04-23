# pylint: disable=W5101

"""
    Representação do opcional(add ons)
"""

from .optional_interface import OptionalInterface


class OptionalProduct(OptionalInterface):

    def __str__(self):
        return self.description
