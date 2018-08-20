from addon.models import Product, Service
from core.specification import CompositeSpecification
from gatheros_event.models import Event
from gatheros_subscription.models import Subscription


class EventSpecificationMixin(CompositeSpecification):
    """
        Esse mixin que garante que o candidato repassado via o metodo
        'is_satisfied_by' seja uma instancia de Event, além de oferecer uns
        metodos privados que são compartilhados por seus filhos
    """

    @staticmethod
    def _is_event_instance(event):
        if not isinstance(event, Event):
            raise ValueError('event não é uma instancia de Event')

    @staticmethod
    def _get_valid_subs_in_lot(lot):
        return Subscription.objects.filter(
            lot=lot,
            completed=True,
            test_subscription=False,
        ).exclude(
            subscription__status=Subscription.CANCELED_STATUS
        )

    @staticmethod
    def _get_active_products_in_lot(lot):
        return Product.objects.filter(
            lot_category=lot.category,
            published=True,
        )

    @staticmethod
    def _get_active_services_in_lot(lot):
        return Service.objects.filter(
            lot_category=lot.category,
            published=True,
        )

    def is_satisfied_by(self, event: Event):
        self._is_event_instance(event)
