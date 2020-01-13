""" Signals do model `addons` """

from django.db.models.signals import post_save
from django.dispatch import receiver

from gatheros_subscription.models import Subscription, Lot


@receiver(post_save, sender=Subscription)
def clean_addon_when_lot_change(instance, raw, created, **_):
    """
     Limpa inscrições de opcionais se lote da inscrição mudar.
     """

    if raw is True or created is True:
        return

    if instance.has_changed('lot_id') is True:
        # Se lote mudou
        for addon in instance.subscription_products.all():
            addon.delete()

        for addon in instance.subscription_services.all():
            addon.delete()
