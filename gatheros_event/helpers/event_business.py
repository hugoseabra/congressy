"""
    Esses helpers tem como objetivo identificar o tipo do evento:

        - Grátis
        - Pago

    Além de também mudar o tipo do evento e aplicar as configuração das features
    disponiveis de acordo com o tipo em si

"""
from decimal import Decimal

from addon.models import Product, Service
from gatheros_event.event_state import EventState
from gatheros_event.models import Event
from gatheros_subscription.models import Lot, LotCategory, Subscription


def is_free_event(event: Event):
    if not isinstance(event, Event):
        raise Exception("{} '{}' não é uma instancia de Event".format(
            event,
            event.__class__,
        ))

    return EventState(event).is_free()


def is_paid_event(event: Event):
    if not isinstance(event, Event):
        raise Exception("{} '{}' não é uma instancia de Event".format(
            event,
            event.__class__,
        ))

    return EventState(event).is_payable()


def event_has_had_payment(event: Event) -> bool:
    """
    This method looks at *ALL* lots, products and services and evaluates if
    any kind of payment has been made.

    :param event:
    :return: bool
    """
    paid_lots = Lot.objects.filter(
        event=event,
        price__isnull=False,
        price__gt=0,
    )

    paid_products = Product.objects.filter(
        lot_category__event=event,
        liquid_price__gt=Decimal(0.00),
    )

    paid_service = Service.objects.filter(
        lot_category__event=event,
        liquid_price__gt=Decimal(0.00),
    )

    if paid_lots.count() == 0 and paid_products == 0 and paid_service == 0:
        return False

    for lot in paid_lots.all():
        if lot_has_confirmed_subscription(lot=lot):
            return True

    for product in paid_products.all():
        if lot_has_confirmed_subscription(product.lot_category):
            return True

    for service in paid_service.all():
        if lot_has_confirmed_subscription(service.lot_category):
            return True

    return False


def lot_category_has_confirmed_subscription(lot_cat: LotCategory) -> bool:
    """

    This method looks at subscriptions in each lot in this lot category and
    evaluates if has any confirmed subscriptions.

    :param lot_cat: LotCategory object
    :return: bool
    """

    for lot in lot_cat.lots.all():

        if lot_has_confirmed_subscription(lot):
            return True

    return False


def lot_has_confirmed_subscription(lot: Lot) -> bool:
    """

    This method looks at subscriptions in lot  evaluates if has any
    confirmed subscriptions.

    :param lot: Lot Object
    :return: bool
    """

    subs_lots = Subscription.objects.filter(
        lot=lot,
        test_subscription=False,
        status=Subscription.CONFIRMED_STATUS,
    )

    if subs_lots.count() == 0:
        return False

    return True
