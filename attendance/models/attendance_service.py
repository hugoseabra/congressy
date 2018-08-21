from django.db import models
from gatheros_event.models import Event


class AttendanceService(models.Model):
    name = models.CharField(max_length=255, verbose_name='nome')

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name='evento',
        related_name='attendance_services'
    )

    created_on = models.DateTimeField(auto_now_add=True,
                                      verbose_name='criado em')

    class Meta:
        verbose_name = 'Lista de Check-in/out'
        verbose_name_plural = 'Lista de Check-ins/outs'
        ordering = ['name']
