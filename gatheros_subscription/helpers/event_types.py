"""
    Esses helpers tem como objetivo identificar o tipo do evento:

        - Grátis
        - Pago

    Além de também mudar o tipo do evento e aplicar as configuração das features
    disponiveis de acordo com o tipo em si
        
"""
from gatheros_event.models import Event
from gatheros_event.event_state import EventState


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


def change_event_type(event: Event):
    feature_config = event.feature_configuration

    if is_paid_event(event) and \
            feature_config.last_updated_by == feature_config.SYSTEM_USER_NAME:

        if event.event_type is not event.EVENT_TYPE_SCIENTIFIC:
            event.event_type = event.EVENT_TYPE_PAID

        for feature, value in PAID_EVENT_FEATURES.items():
                setattr(feature_config, feature, value)

    elif is_free_event(event) and \
            feature_config.last_updated_by == feature_config.SYSTEM_USER_NAME:

        if event.event_type is not event.EVENT_TYPE_SCIENTIFIC:
            event.event_type = event.EVENT_TYPE_FREE

        for feature, value in FREE_EVENT_FEATURES.items():
            setattr(feature_config, feature, value)

    event.save()
    feature_config.save()


FREE_EVENT_FEATURES = {
    # Before event
    'feature_survey': True,
    'feature_certificate': True,
    'feature_products': True,
    'feature_services': True,
    'feature_internal_subscription': True,
    'feature_boleto_expiration_on_lot_expiration': False,
    'feature_import_via_csv': False,
    # During Event
    'feature_manual_payments': False,
    'feature_checkin': True,
}


PAID_EVENT_FEATURES = {
    # Before event
    'feature_survey': True,
    'feature_certificate': True,
    'feature_products': True,
    'feature_services': True,
    'feature_internal_subscription': True,
    'feature_boleto_expiration_on_lot_expiration': False,
    'feature_import_via_csv': False,
    # During Event
    'feature_manual_payments': False,
    'feature_checkin': True,
}
