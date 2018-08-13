"""
    Esses helpers tem como objetivo identificar o tipo do evento:

        - Grátis
        - Pago
        
"""
from gatheros_event.models import Event


def is_free_event(event: Event):

    if not isinstance(event, Event):
        raise Exception("{} '{}' não é uma instancia de Event".format(
            event,
            event.__class__,
        ))

    lots = event.lots.all()

    for lot in lots:

        if lot.price and lot.price > 0:
            return False

        if hasattr(lot, 'category') and lot.category is not None:

            category = lot.category
            services = category.service_optionals
            products = category.product_optionals

            if services is not None:
                for service in services.all():
                    if service.liquid_price > 0:
                        return False

            if products is not None:
                for product in products.all():
                    if product.liquid_price > 0:
                        return False

    return True


def is_paid_event(event: Event):
    return not is_free_event(event)


def event_has_products(event: Event):

    if not isinstance(event, Event):
        raise Exception("{} '{}' não é uma instancia de Event".format(
            event,
            event.__class__,
        ))

    lots = event.lots.all()

    for lot in lots:

        if hasattr(lot, 'category') and lot.category is not None:

            category = lot.category
            products = category.product_optionals

            if products is not None:
                if products.all().count() > 0:
                    return True

    return False


def event_has_services(event: Event):

    if not isinstance(event, Event):
        raise Exception("{} '{}' não é uma instancia de Event".format(
            event,
            event.__class__,
        ))

    lots = event.lots.all()

    for lot in lots:

        if hasattr(lot, 'category') and lot.category is not None:

            category = lot.category
            services = category.service_optionals

            if services is not None:
                if services.all().count() > 0:
                    return True
                
    return False
