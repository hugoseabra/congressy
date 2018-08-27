""" Signals do model `addons` """
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from addon.models import Service, Product
from gatheros_event.signals.helpers import update_event_config_flags


@receiver(post_save, sender=Product)
@receiver(post_save, sender=Service)
@receiver(pre_delete, sender=Product)
@receiver(pre_delete, sender=Service)
def set_feature_flags_on_event_type_change(instance, **_):
    """ Altera as flags de fatures quando um evento muda de tipo """

    event = instance.lot_category.event
    update_event_config_flags(event)
