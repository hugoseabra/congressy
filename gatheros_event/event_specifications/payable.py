from decimal import Decimal

from core.specification import AndSpecification
from gatheros_event.models import Event
from gatheros_subscription.models import Lot
from .mixins import EventCompositeSpecificationMixin, \
    LotCompositeSpecificationMixin
from .visible import LotVisible


class EventPayable(EventCompositeSpecificationMixin):
    """
        Essa especificação informa se o evento possui algum lote ou algum
        opcional, produto ou serviço ativo e que ainda pode ser pago, ou seja
        no presente ou no passado.
    """

    def is_satisfied_by(self, event: Event):
        super().is_satisfied_by(event)

        for lot in event.lots.all():

            one = LotVisible()
            other = LotPayable()

            spec = AndSpecification(one, other)

            if spec.is_satisfied_by(lot):
                return True

        return False


class LotPayable(LotCompositeSpecificationMixin):
    """
        Essa especificação informa se o lote ou algum opcional, produto ou
        serviço ativo vinculado ao lote.
    """

    def is_satisfied_by(self, lot: Lot):
        super().is_satisfied_by(lot)

        if lot.price and lot.price > 0:
            return True

        # Products
        all_products = self._get_active_products_in_lot(lot)
        for product in all_products:

            if not product.running:
                continue

            if product.has_quantity_conflict or \
                    product.has_sub_end_date_conflict:
                continue
            if product.price > Decimal(0.00):
                return True

        # Services
        all_services = self._get_active_services_in_lot(lot)
        for service in all_services:

            if not service.running:
                continue

            if service.has_quantity_conflict or \
                    service.has_sub_end_date_conflict:
                continue

            if service.price > Decimal(0.00):
                return True

        return False
