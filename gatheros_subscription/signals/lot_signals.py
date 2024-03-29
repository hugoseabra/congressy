""" Signals do model `lot` """
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from gatheros_event.signals.helpers import (
    update_event_config_flags,
    update_event_publishing,
)
from gatheros_subscription.models import Lot


@receiver(pre_delete, sender=Lot)
@receiver(post_save, sender=Lot)
def set_feature_flags_on_event_type_change(instance, **_):
    """ Altera as flags de fatures quando um evento muda de tipo """

    event = instance.event
    update_event_config_flags(event)
    update_event_publishing(event)
