from django.db import models

from base.models import EntityMixin
from core.model import track_data
from gatheros_subscription.models import Subscription
from . import AttendanceService


class Attendance(models.Model, EntityMixin):
    class Meta:
        abstract = True
        ordering = ['created_on']

        indexes = [models.Index(fields=['created_by', ])]

    created_on = models.DateTimeField(
        verbose_name='imprimiu a etiqueta em',
        null=True,
        blank=True,
        auto_now_add=True,
    )

    created_by = models.CharField(
        max_length=255,
        verbose_name='criado por'
    )

    registration = models.DateTimeField(
        verbose_name='tempo informado pelo organizador',
        null=True,
        blank=True,
    )


@track_data('printed_on', )
class Checkin(Attendance):
    class Meta(Attendance.Meta):
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


@track_data('checkin', )
class Checkout(Attendance):
    class Meta(Attendance.Meta):
        verbose_name = 'saída'
        verbose_name_plural = 'saídas'

    checkin = models.OneToOneField(
        Checkin,
        on_delete=models.CASCADE,
        verbose_name='Check-in',
        related_name='checkout'
    )
