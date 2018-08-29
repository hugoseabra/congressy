from django.db import models

from gatheros_subscription.models import Subscription
from . import AttendanceService


class Attendance(models.Model):
    class Meta:
        abstract = True
        ordering = ['created_on']

        indexes = [models.Index(fields=['attended_by', ])]

    created_on = models.DateTimeField(
        verbose_name='imprimiu a etiqueta em',
        null=True,
        blank=True,
        auto_now_add=True,
    )

    attended_by = models.CharField(
        max_length=255,
        verbose_name='criado por'
    )


class Checkin(Attendance):
    class Meta (Attendance.Meta):
        verbose_name = 'entrada'
        verbose_name_plural = 'entradas'

    attendance_service = models.ForeignKey(
        AttendanceService,
        verbose_name='Lista de Check-in/out',
        related_name='checkins',
        on_delete=models.CASCADE
    )

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        verbose_name='Inscrito',
        related_name='checkins'
    )

    printed_on = models.DateTimeField(
        verbose_name='imprimiu a etiqueta em',
        null=True,
        blank=True
    )


class Checkout(Attendance):
    class Meta (Attendance.Meta):
        verbose_name = 'saída'
        verbose_name_plural = 'saídas'

    checkin = models.OneToOneField(
        Checkin,
        on_delete=models.CASCADE,
        verbose_name='Check-in',
        related_name='checkout'
    )
