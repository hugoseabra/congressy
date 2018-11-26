from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from installment.models import Contract, Part
from payment.models import Transaction


@receiver(post_save, sender=Part)
def set_contract_status(instance, raw, created, **_):
    # Disable when loaded by fixtures
    if raw is True or created is True:
        return

    contract = instance.contract

    if contract.status == Contract.CANCELLED_STATUS:
        return

    if instance.has_changed('paid') is False:
        return

    has_all_paid = True

    for part in contract.parts.all():
        if part.paid is False:
            has_all_paid = False

    if has_all_paid is True:
        contract.status = Contract.FULLY_PAID_STATUS
    else:
        contract.status = Contract.OPEN_STATUS

    contract.save()

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
