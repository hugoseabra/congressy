from django.db import models

from base.models import EntityMixin
from core.model import track_data
from gatheros_event.models import Event


@track_data('name', 'checkout_enabled', 'with_certificate', 'accreditation')
class AttendanceService(models.Model, EntityMixin):
    name = models.CharField(max_length=255, verbose_name='nome do atendimento')

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name='evento',
        related_name='attendance_services'
    )

    created_on = models.DateTimeField(auto_now_add=True,
                                      verbose_name='criado em',
                                      editable=False,)
    modified_on = models.DateTimeField(auto_now=True,
                                       verbose_name='modificado em',
                                       editable=False,)

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

    def __str__(self):
        return self.name

    accreditation = models.BooleanField(
        default=False,
        verbose_name='Credenciamento principal',
        help_text='Este é o serviço de credenciamento? O evento só poderá ter'
                  ' um.'

    )

    class Meta:
        verbose_name = 'Lista de Check-in/out'
        verbose_name_plural = 'Lista de Check-ins/outs'
        ordering = ['name']
