from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from installment.models import Part
from payment.models import Transaction


@receiver(post_save, sender=Transaction)
def set_part_paid_flag(instance, **kwargs):
    # Disable when loaded by fixtures
    if not kwargs.get('created', False) or kwargs.get('raw', False):
        return

    if not instance.part_id:
        return

    if instance.part.paid:
        return

    total_paid = 0

    part_transactions = instance.part.transactions.filter(
        status=Transaction.PAID,
    )

    if part_transactions.count() == 0:
        return

    for trans in part_transactions:
        total_paid += trans.amount

    instance.part.paid = total_paid >= instance.part.amount
    instance.part.save()


@receiver(post_delete, sender=Transaction)
def set_part_unpaid_flag(instance, **kwargs):
    # Disable when loaded by fixtures
    if kwargs.get('raw', False):
        return

    if not instance.part_id:
        return

    instance.part.paid = False
    instance.part.save()
