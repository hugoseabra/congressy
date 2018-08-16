""" Signals do model `lot` """
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from gatheros_subscription.helpers.event_types import change_event_type
from gatheros_subscription.models import Lot


@receiver(post_save, sender=Lot)
@receiver(pre_delete, sender=Lot)
def set_feature_flags_on_event_type_change(instance, **_):
    """ Altera as flags de fatures quando um evento muda de tipo """

    event = instance.event
    change_event_type(event)
