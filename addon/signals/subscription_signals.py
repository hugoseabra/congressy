""" Signals do model `addons` """

from django.db.models.signals import post_save
from django.dispatch import receiver

from gatheros_subscription.models import Subscription, Lot


@receiver(post_save, sender=Subscription)
def clean_addon_when_lot_cat_subscription_change(instance, raw, created, **_):
    """
     Limpa inscrições de opcionais se o categoria vinculada ao lote anterior
     também mudar.
     """

    if raw is True or created is True:
        return

    if instance.has_changed('lot_id') is True:
        # Se lote mudou
        old_lot = Lot.objects.get(pk=instance.old_value('lot_id'))
        new_lot = instance.lot

        # Verificar se a categoria mudou
        if old_lot.category_id != new_lot.category_id:
            for addon in instance.subscription_products.all():
                addon.delete()

            for addon in instance.subscription_services.all():
                addon.delete()
