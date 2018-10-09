""" Signals do model `payment.Transaction`. """

from django.db.models.signals import post_save
from django.dispatch import receiver

from mix_boleto.models import SyncBoleto
from payment.models import Transaction
from mix_boleto.mix.sync import MixSync


@receiver(post_save, sender=Transaction)
def trigger_mix_congressy_synchronization(instance, created, raw, **_):
    """ Engatilha sincronzação entre a MixEvents e Congressy. """
    # Disable when loaded by fixtures
    if raw is True and created is True:
        return

    if instance.installment_part >= instance.installments:
        return

    proceed_sync = False

    if instance.has_changed('boleto_url') and instance.boleto_url:
        proceed_sync = True

    if instance.has_changed('status') and instance.status == Transaction.PAID:
        proceed_sync = True

    if proceed_sync is True:

        try:
            sync_boleto = SyncBoleto.objects.get(
                cgsy_transaction_id=instance.pk,
            )

            boleto = sync_boleto.mix_boleto

            synchronizer = MixSync(
                resource_alias=boleto.sync_resource.alias,
                event_id=instance.subscription.event_id,
            )

            synchronizer.prepare(boleto.mix_subscription_id)
            synchronizer.run()

        except SyncBoleto.DoesNotExist:
            pass
