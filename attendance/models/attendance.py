from django.db import models
from . import AttendanceService
from gatheros_subscription.models import Subscription


class Attendance(models.Model):
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        verbose_name='Inscrito',
        related_name='%(class)ss'
    )

    attended_on = models.DateTimeField(
        verbose_name='imprimiu a etiqueta em',
        null=True,
        blank=True,
        auto_now_add=True,
    )

    attended_by = models.PositiveIntegerField(verbose_name='criado por')

    attendance_service = models.ForeignKey(
        AttendanceService,
        verbose_name='Lista de Check-in/out',
        related_name='%(class)ss',
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendances'
        ordering = ['attended_on']

        indexes = [models.Index(fields=['attended_by', ])]


class Checkin(Attendance):

    printed_on = models.DateTimeField(
        verbose_name='imprimiu a etiqueta em',
        null=True,
        blank=True
    )


class Checkout(Attendance):

    checkin = models.OneToOneField(
        Checkin,
        on_delete=models.CASCADE,
        verbose_name='Check-in',
        related_name='checkout'
    )

