from django.db import models
from . import AttendanceService
from addon.models.optional_type import OptionalServiceType


class AttendanceServiceFilter(models.Model):

    service = models.ForeignKey(
        OptionalServiceType,
        on_delete=models.CASCADE,
        verbose_name='Tipo de opcional de serviço',
        related_name='service_filters'
    )

    attendance_service = models.ForeignKey(
        AttendanceService,
        verbose_name='Lista de Check-in/out',
        related_name='service_filters',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Filtro para lista de Check-In/Out por Categoria de Serviço'
        ordering = ['attendance_service', ]

