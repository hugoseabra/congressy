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
