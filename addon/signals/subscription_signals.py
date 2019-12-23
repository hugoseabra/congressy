""" Signals do model `addons` """
import os
import shutil

from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver

from addon.models import Service, Product
from gatheros_event.signals.helpers import (
    update_event_config_flags,
    update_event_publishing,
)
from gatheros_subscription.models import Subscription


@receiver(post_save, sender=Subscription)
def clean_addon_when_subscription_change(instance, raw, created, **_):
    """ Limpa inscrições de opcionais se o lote for mudado. """

    if raw is True or created is True:
        return

    if instance.has_changed('lot_id') is True:
        for addon in instance.subscription_products.all():
            addon.delete()

        for addon in instance.subscription_services.all():
            addon.delete()
