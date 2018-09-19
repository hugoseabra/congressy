from django.db.models.signals import post_save
from django.dispatch import receiver

from attendance.models import AttendanceService
from gatheros_event.models import Event


@receiver(post_save, sender=Event)
def create_default_attendance(instance, raw, created, **_):

    if raw is True:
        return

    if created is True:
        AttendanceService.objects.create(
            event=instance,
            name='Credenciamento',
            with_certificate=True,
            checkin_only=True,
        )
