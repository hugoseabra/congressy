from addon.models import Product, Service
from core.specification import CompositeSpecification, AndSpecification
from gatheros_event.models import Event
from gatheros_subscription.models import Subscription, Lot


class EventCompositeSpecificationMixin(CompositeSpecification):
    """
        Esse mixin que garante que o candidato repassado via o metodo
        'is_satisfied_by' seja uma instancia de Event
    """

    @staticmethod
    def _is_event_instance(event):
        if not isinstance(event, Event):
            raise ValueError('event não é uma instancia de Event')

    def is_satisfied_by(self, event: Event):
        self._is_event_instance(event)
        return super().is_satisfied_by(event)


class EventAndSpecificationMixin(AndSpecification):
    """
        Esse mixin que garante que o candidato repassado via o metodo
        'is_satisfied_by' seja uma instancia de Event
    """

    @staticmethod
    def _is_event_instance(event):
        if not isinstance(event, Event):
            raise ValueError('event não é uma instancia de Event')

    def is_satisfied_by(self, event: Event):
        self._is_event_instance(event)
        return super().is_satisfied_by(event)


class LotCompositeSpecificationMixin(CompositeSpecification):
    """
        Esse mixin que garante que o candidato repassado via o metodo
        'is_satisfied_by' seja uma instancia de Lote, além de oferecer uns
        metodos privados que são compartilhados por seus filhos
    """

    """
        Esse mixin que garante que o candidato repassado via o metodo
        'is_satisfied_by' seja uma instancia de Lote, além de oferecer uns
        metodos privados que são compartilhados por seus filhos
    """

    @staticmethod
    def _is_lot_instance(lot):
        if not isinstance(lot, Lot):
            raise ValueError('lot não é uma instancia de Lot')

    @staticmethod
    def _get_valid_subs_in_lot(lot):
        return Subscription.objects.filter(
            lot=lot,
            completed=True,
            test_subscription=False,
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

    def is_satisfied_by(self, lot: Lot):
        self._is_lot_instance(lot)
        return super().is_satisfied_by(lot)
