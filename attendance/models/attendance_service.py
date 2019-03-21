from django.db import models

from gatheros_event.models import Event


class AttendanceService(models.Model):
    name = models.CharField(max_length=255, verbose_name='nome do atendimento')

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name='evento',
        related_name='attendance_services'
    )

    created_on = models.DateTimeField(auto_now_add=True,
                                      verbose_name='criado em')

    checkout_enabled = models.BooleanField(
        default=False,
        verbose_name='Registrar horas?',
        help_text="O atendimento irá contabilizar as horas em que o"
                  " participante ficou presente no atendimento."
    )

    with_certificate = models.BooleanField(
        default=False,
        verbose_name='Atendimento com certificado',
        help_text='Esse atendimento terá direito a certificado ?'

    )

    printing_queue_webhook = models.TextField(
        verbose_name='Webhook de fila de impressão',
        help_text='Use o endereço completo incluindo http(s)://',
        null=True,
        blank=True,
    )

    printer_number = models.PositiveIntegerField(
        verbose_name='Núm. impressora',
        null=True,
        blank=True,
    )

    pwa_pin = models.CharField(
        max_length=12,
        verbose_name='PIN de acesso',
        help_text='Acesso ao aplicativo PWA',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Lista de Check-in/out'
        verbose_name_plural = 'Lista de Check-ins/outs'
        ordering = ['name']
