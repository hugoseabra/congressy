from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from payment.models import Transaction


@receiver(post_save, sender=Transaction)
def set_part_paid_flag(instance, **kwargs):
    # Disable when loaded by fixtures
    if kwargs.get('raw', False):
        return

    if instance.part_transaction and kwargs.get('created', False):
        instance.part_transaction.paid = \
            instance.amount >= instance.part_transaction.amount
        instance.part_transaction.save()


@receiver(post_delete, sender=Transaction)
def set_part_unpaid_flag(instance, **kwargs):
    # Disable when loaded by fixtures
    if kwargs.get('raw', False):
        return

    if instance.part_transaction:
        part = instance.part_transaction
        part.paid = False
        part.transaction = None
        part.save()
