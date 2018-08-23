from django.db import models
from . import AttendanceService
from gatheros_subscription.models import Subscription


class Attendance(models.Model):
    CHECK_IN = 'check-in'
    CHECK_OUT = 'check-out'

    OPERATION_OPTIONS = (
        (CHECK_IN, 'check-in'),
        (CHECK_OUT, 'check-out')
    )

    operation = models.CharField(
        choices=OPERATION_OPTIONS,
        max_length=35,
        verbose_name='Tipo de Operação',
        help_text='Tipo de operação (check-in, check-out'
    )

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        verbose_name='Inscrito',
        related_name='attendances'
    )

    created_on = models.DateTimeField(auto_now_add=True,
                                      verbose_name='criado em')

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
        ordering = ['created_on']

        indexes = [models.Index(fields=['attended_by', ])]
