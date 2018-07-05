# pylint: disable=W5101


from django.db import models

from . import Event


class ConfFeatureRelease(models.Model):
    """ Configuração de Recursos liberados de um evento """

    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name='evento',
        related_name='feature_release',
    )

    feature_survey = models.BooleanField(
        default=True,
        name='funcionalidade - form. personalizado',
        help_text='Liberar funcionalidade de formulário personalizado no'
                  ' evento.'
    )

    feature_checkin = models.BooleanField(
        default=True,
        name='funcionalidade - check-in',
        help_text='Liberar funcionalidade de check-in no evento.'
    )

    feature_certificate = models.BooleanField(
        default=True,
        name='funcionalidade - certificado',
        help_text='Liberar funcionalidade de certificado no evento.'
    )

    feature_products = models.BooleanField(
        default=True,
        name='funcionalidade - opcionais',
        help_text='Liberar funcionalidade de opcionais no evento.'
    )

    feature_services = models.BooleanField(
        default=True,
        name='funcionalidade - atividades extras',
        help_text='Liberar funcionalidade de atividades extras no evento.'
    )
