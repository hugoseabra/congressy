""" Signals do model `addons` """

from django.db.models.signals import post_save
from django.dispatch import receiver

from gatheros_subscription.models import Subscription
from payment_debt.models import Debt


@receiver(post_save, sender=Subscription)
def clean_addon_when_lot_subscription_change(instance, raw, created, **_):
    """
     Limpa despesas de opcionais quando lote da inscrição mudar para que possam
     ser recriadas no processamento de pagamento.
     """

    if raw is True or created is True:
        return

    if instance.has_changed('lot_id') is True:
        # Se lote mudou
        Debt.objects.filter(subscription_id=instance.pk).delete()


@receiver(post_save, sender=Subscription)
def clean_addon_when_lot_subscription_change(instance, raw, created, **_):
    """
     Limpa despesas de opcionais quando lote da inscrição mudar para que possam
     ser recriadas no processamento de pagamento.
     """

    if raw is True or created is True:
        return

    if instance.has_changed('lot_id') is True:
        # Se lote mudou
        qs = Debt.objects.filter(subscription_id=instance.pk)
        if qs.count():
            qs.delete()
