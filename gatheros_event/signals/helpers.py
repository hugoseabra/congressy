"""
    Esses helpers são para uso apenas de signals
"""
from gatheros_event.constants import PAID_EVENT_FEATURES, FREE_EVENT_FEATURES
from gatheros_event.helpers.event_business import is_paid_event, is_free_event
from gatheros_event.models import Event


def _has_only_first_lot_active(event: Event):
    found_active_lot = False

    for lot in event.lots.all():
        if not found_active_lot and lot.active:
            found_active_lot = True
        elif found_active_lot and lot.active:
            return False

    return True


def _deactivate_all_but_first_lot(event: Event):
    for lot in event.lots.all():
        lot.active = False
        lot.save()

    first_lot = event.lots.all().first()
    first_lot.active = True
    first_lot.save()


def update_event_config_flags(event: Event):
    """
        Esse helper atualiza as flags dos eventos de acordo com as regras de
        business.
    """
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

        if not _has_only_first_lot_active(event):
            _deactivate_all_but_first_lot(event)

    event.save()
    feature_config.save()
