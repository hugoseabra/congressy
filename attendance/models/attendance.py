from django.db import models
from . import AttendanceService
from gatheros_subscription.models import Subscription


class Attendance(models.Model):
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        verbose_name='Inscrito',
        related_name='attendances'
    )

    checkin_on = models.DateTimeField(null=True,
                                      blank=True,
                                      verbose_name='check-in realizado em')

    checkout_on = models.DateTimeField(null=True,
                                       blank=True,
                                       verbose_name='check-out realizado em')

    attended_by = models.PositiveIntegerField(verbose_name='criado por')

    attendance_service = models.ForeignKey(
        AttendanceService,
        verbose_name='Lista de Check-in/out',
        related_name='attendances',
        on_delete=models.CASCADE
    )

    printed_on = models.DateTimeField(
        verbose_name='imprimiu a etiqueta em',
        null=True,
        blank=True
    )

    printed = models.BooleanField(
        default=False,
        verbose_name='imprimiu etiqueta'
    )

    class Meta:
        verbose_name = 'Check-in/out'
        verbose_name_plural = 'Check-ins/outs'
        ordering = ['checkin_on']

        indexes = [models.Index(fields=['attended_by', ])]
