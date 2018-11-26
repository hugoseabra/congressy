from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from payment.models import Transaction


@receiver(post_save, sender=Transaction)
def set_part_paid_flag(instance, created, raw, **_):
    # Disable when loaded by fixtures
    if raw is True or created is True:
        return

    if instance.installment_part and created:
        instance.installment_part.paid = \
            instance.amount >= instance.installment_part.amount
        instance.installment_part.save()


@receiver(post_delete, sender=Transaction)
def set_part_unpaid_flag(instance, created, raw, **_):
    # Disable when loaded by fixtures
    if raw is True or created is True:
        return

    if instance.installment_part:
        instance.installment_part.paid = False
        instance.installment_part.save()
