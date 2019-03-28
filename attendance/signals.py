from datetime import datetime
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from attendance.models import AttendanceService, Checkin, Checkout
from gatheros_event.models import Event


@receiver(post_save, sender=Event)
def create_default_attendance(instance, raw, created, **_):
    if raw is True:
        return

    if created is True:
        AttendanceService.objects.create(
            event=instance,
            name='Credenciamento',
            accreditation=True,
            with_certificate=True,
            checkout_enabled=False,
        )


@receiver(pre_save, sender=Checkin)
def register_subscription_as_attended(instance, raw, **_):
    if raw is True:
        return

    service = instance.attendance_service

    if service.accreditation is False:
        return

    sub = instance.subscription
    sub.accredited = True
    sub.accredited_on = datetime.now()
    sub.save()


@receiver(pre_save, sender=Checkout)
def register_subscription_as_not_attended(instance, raw, **_):
    if raw is True:
        return

    checkin = instance.checkin
    service = checkin.attendance_service

    if service.accreditation is False:
        return

    sub = checkin.subscription
    sub.accredited = False
    sub.accredited_on = datetime.now()
    sub.save()
