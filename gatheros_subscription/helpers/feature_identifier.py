"""
    Esses helpers tem como objetivo identificar o tipo do evento:

        - Grátis
        - Pago
        - Cientifico
"""
from gatheros_event.models import Event


def is_free_event(event: Event):
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
