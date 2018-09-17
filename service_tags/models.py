# pylint: disable=W5101
"""
Models de certificados
"""

from django.db import models


class CustomServiceTag(models.Model):
    """ Certificado de evento."""

    class Meta:
        verbose_name = 'Script customizado'
        verbose_name_plural = 'Scripts customizados'

    event = models.OneToOneField(
        'gatheros_event.Event',
        on_delete=models.CASCADE,
        verbose_name='evento',
        related_name='custom_service_tag'
    )

    tracking_script = models.TextField(
        verbose_name='Scripts de Rastreamento',
        help_text='Códigos para serem carregar em páginas diversas.',
        null=True,
        blank=True,
    )

    conversion_script = models.TextField(
        verbose_name='Scripts de Conversão de Inscrição',
        help_text='Códigos para serem carregados após finalizar uma'
                  ' inscrição.',
        null=True,
        blank=True,
    )
