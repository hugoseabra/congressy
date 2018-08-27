"""
    Esses helpers são para uso apenas de signals
"""
from gatheros_event.constants import PAID_EVENT_FEATURES, FREE_EVENT_FEATURES
from gatheros_event.helpers.event_business import is_paid_event, is_free_event
from gatheros_event.models import Event


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
        event.lots.all().update(
            active=False,
        )

    event.save()
    feature_config.save()
