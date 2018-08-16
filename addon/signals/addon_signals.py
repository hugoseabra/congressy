""" Signals do model `addons` """
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from addon.models import Service, Product
from gatheros_subscription.helpers.event_types import change_event_type


@receiver(post_save, sender=Product)
@receiver(post_save, sender=Service)
@receiver(pre_delete, sender=Product)
@receiver(pre_delete, sender=Service)
def set_feature_flags_on_event_type_change(instance, **_):
    """ Altera as flags de fatures quando um evento muda de tipo """

    event = instance.lot_category.event
    change_event_type(event)
