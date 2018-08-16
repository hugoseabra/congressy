"""
    Esses helpers tem como objetivo identificar o tipo do evento:

        - Grátis
        - Pago

    Além de também mudar o tipo do evento e aplicar as configuração das features
    disponiveis de acordo com o tipo em si
        
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


def change_event_type(event: Event):
    feature_config = event.feature_configuration

    if is_paid_event(event):

        if event.event_type is not event.EVENT_TYPE_SCIENTIFIC:
            event.event_type = event.EVENT_TYPE_PAID

        for feature, value in PAID_EVENT_FEATURES.items():
            setattr(feature_config, feature, value)

    elif is_free_event(event):

        if event.event_type is not event.EVENT_TYPE_SCIENTIFIC:
            event.event_type = event.EVENT_TYPE_FREE

        for feature, value in FREE_EVENT_FEATURES.items():
            setattr(feature_config, feature, value)

    event.save()
    feature_config.save()


FREE_EVENT_FEATURES = {
    'feature_survey': True,
    'feature_checkin': True,
    'feature_certificate': True,
    'feature_products': False,
    'feature_services': False,
    'feature_internal_subscription': True,
    'feature_manual_payments': False,
    'feature_boleto_expiration_on_lot_expiration': False,
    'feature_import_via_csv': False,
}


PAID_EVENT_FEATURES = {
    'feature_survey': True,
    'feature_checkin': True,
    'feature_certificate': True,
    'feature_products': True,
    'feature_services': True,
    'feature_internal_subscription': True,
    'feature_manual_payments': False,
    'feature_boleto_expiration_on_lot_expiration': True,
    'feature_import_via_csv': False,
}
