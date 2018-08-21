from django.db import models
from . import attendance_service
from addon.models.optional_type import OptionalProductType


class AttendanceProductFilter(models.Model):

    product = models.ForeignKey(
        OptionalProductType,
        on_delete=models.CASCADE,
        verbose_name='Tipo de opcional de produto',
        related_name='product_filters'
    )

    attendance_service = models.ForeignKey(
        attendance_service,
        verbose_name='Lista de Check-in/out',
        related_name='product_filters',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Filtro para lista de Check-In/Out por Categoria de Produto'
        ordering = ['attendance_service',]

