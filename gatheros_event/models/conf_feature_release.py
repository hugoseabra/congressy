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
        default=False,
        verbose_name='funcionalidade - form. personalizado',
        help_text='Liberar funcionalidade de formulário personalizado no'
                  ' evento.'
    )

    feature_checkin = models.BooleanField(
        default=False,
        verbose_name='funcionalidade - check-in',
        help_text='Liberar funcionalidade de check-in no evento.'
    )

    feature_certificate = models.BooleanField(
        default=False,
        verbose_name='funcionalidade - certificado',
        help_text='Liberar funcionalidade de certificado no evento.'
    )

    feature_products = models.BooleanField(
        default=False,
        verbose_name='funcionalidade - opcionais',
        help_text='Liberar funcionalidade de opcionais no evento.'
    )

    feature_services = models.BooleanField(
        default=False,
        verbose_name='funcionalidade - atividades extras',
        help_text='Liberar funcionalidade de atividades extras no evento.'
    )
