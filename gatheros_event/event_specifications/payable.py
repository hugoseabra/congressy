from decimal import Decimal

from django.db.models import Count

from addon.models import Product, Service
from core.specification import AndSpecification
from gatheros_event.models import Event, Organization
from gatheros_subscription.models import Lot, Subscription
from .mixins import (
    EventCompositeSpecificationMixin,
    LotCompositeSpecificationMixin,
    ProductCompositeSpecificationMixin,
    ServiceCompositeSpecificationMixin,
    OrganizationCompositeSpecificationMixin,
)
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

        if EventHasHadTransactions().is_satisfied_by(event):
            return True

        return False


class LotPayable(LotCompositeSpecificationMixin):
    """
        Essa especificação informa se o lote ou algum opcional, produto ou
        serviço ativo vinculado ao lote.
    """

    def is_satisfied_by(self, lot: Lot):
        super().is_satisfied_by(lot)

        paid_service_or_product_flag = False

        # Products
        all_products = self._get_active_products_in_lot(lot)
        for product in all_products:

            if ProductPayable().is_satisfied_by(product):
                paid_service_or_product_flag = True

        # Services
        all_services = self._get_active_services_in_lot(lot)
        for service in all_services:

            if ServicePayable().is_satisfied_by(service):
                paid_service_or_product_flag = True

        if not paid_service_or_product_flag and not lot.price or lot.price == 0:
            return False

        return True


class ProductPayable(ProductCompositeSpecificationMixin):
    """
        Essa especificação informa se o  produto é possivel ser pago
    """

    def is_satisfied_by(self, product: Product):
        super().is_satisfied_by(product)

        if not product.running:
            return False

        if product.has_quantity_conflict or \
                product.has_sub_end_date_conflict:
            return False

        if product.price == Decimal(0.00):
            return False

        return True


class ServicePayable(ServiceCompositeSpecificationMixin):
    """
        Essa especificação informa se o serviço é possivel ser pago
    """

    def is_satisfied_by(self, service: Service):
        super().is_satisfied_by(service)

        if not service.running:
            return False

        if service.has_quantity_conflict or \
                service.has_sub_end_date_conflict:
            return False

        if service.price == Decimal(0.00):
            return False

        return True


class EventHasHadTransactions(EventCompositeSpecificationMixin):
    """
        Essa especificação informa se o evento já possuiu algum lote ou algum
        opcional, produto ou serviço
    """

    def is_satisfied_by(self, event: Event):
        super().is_satisfied_by(event)

        return Subscription.objects.annotate(
            num_transactions=Count('transactions')
        ).filter(
            event=event,
            num_transactions__gt=0,
        ).count() > 0


class OrganizationHasBanking(OrganizationCompositeSpecificationMixin):

    def is_satisfied_by(self, organization: Organization):
        super().is_satisfied_by(organization)

        banking_required_fields = [
            'bank_code',
            'agency',
            'account',
            'cnpj_ou_cpf',
            'account_type',
        ]

        for field in Organization._meta.get_fields():

            for required_field in banking_required_fields:

                if field.name == required_field:

                    if not getattr(organization, field.name):
                        return False

        return True
