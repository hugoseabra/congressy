from django.db import models
from . import AttendanceService
from gatheros_subscription.models import LotCategory


class AttendanceCategoryFilter(models.Model):

    lot_category = models.ForeignKey(
        LotCategory,
        on_delete=models.CASCADE,
        verbose_name='Categoria',
        related_name='attendance_service_filters'
    )

    ticket = models.ForeignKey(
        'ticket.Ticket',
        on_delete=models.CASCADE,
        verbose_name='Ingresso',
        related_name='attendance_service_filters',
        # @TODO - REMOVER E TORNAR OBRIGATÓRIO
        null=True,
        blank=True,
    )

    attendance_service = models.ForeignKey(
        AttendanceService,
        verbose_name='Lista de Check-in/out',
        related_name='lot_category_filters',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Filtro para lista de Check-In/Out por Categoria de' \
                       ' Lote'
        ordering = ['attendance_service']

