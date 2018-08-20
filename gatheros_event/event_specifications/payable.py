from datetime import datetime
from decimal import Decimal

from core.util.date import DateTimeRange
from gatheros_event.models import Event
from .mixins import EventSpecificationMixin


class Payable(EventSpecificationMixin):
    """
        Essa especificação informa se o evento possui algum lote ou algum
        opcional, produto ou serviço ativo e que ainda pode ser pago, ou seja
        no presente ou no passado.
    """

    def is_satisfied_by(self, event: Event):
        super().is_satisfied_by(event)

        now = datetime.now()
        for lot in event.lots.filter(active=True):

            # Verificação se o lote está dentro do prazo ativo
            lot_range = DateTimeRange(start=lot.date_start, stop=lot.date_end)
            if now not in lot_range:
                continue

            # Verificação de limite de lote
            total_subs_in_lot = self._get_valid_subs_in_lot(lot)

            if total_subs_in_lot >= lot.limit:
                continue

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
