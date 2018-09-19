from addon.models import Product, Service
from core.specification import Specification
from gatheros_subscription.models import Lot


class Saleable(Specification):

    def is_satisfied_by(self, candidate):

        if isinstance(candidate, Lot):
            return True

        if isinstance(candidate, Product):
            return True

        if isinstance(candidate, Service):
            return True

        return False
