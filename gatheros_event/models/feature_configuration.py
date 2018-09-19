# pylint: disable=W5101


from django.db import models

from . import Event


class FeatureConfiguration(models.Model):
    """ Configuração de Recursos liberados de um evento """

    SYSTEM_USER_NAME = 'system'

    class Meta:
        verbose_name = 'Configuração de Features'
        verbose_name_plural = 'Configurações de Features'

    def __str__(self):
        return self.event.name

    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name='evento',
        related_name='feature_configuration',
    )

    last_updated_by = models.CharField(
        max_length=255,
        verbose_name="atualizado por",
        default=SYSTEM_USER_NAME,
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

    feature_internal_subscription = models.BooleanField(
        default=False,
        verbose_name='funcionalidade - inscrições internas',
        help_text='Liberar funcionalidade de organizadores poderão inserir '
                  'inscrição interna manualmente.'
    )

    feature_manual_payments = models.BooleanField(
        default=False,
        verbose_name='funcionalidade - pagamentos manuais',
        help_text='Liberar funcionalidade de organizadores poderão inserir '
                  'pagamentos manuais.'
    )

    feature_boleto_expiration_on_lot_expiration = models.BooleanField(
        default=False,
        verbose_name='funcionalidade - vencimento dos boletos',
        help_text='Liberar funcionalidade vencimento dos boletos na da data '
                  'de vencimento dos lotes'
    )

    feature_import_via_csv = models.BooleanField(
        default=False,
        verbose_name='funcionalidade - importação via CSV',
        help_text='Liberar funcionalidade de permitir importação via csv'
    )

    feature_multi_lots = models.BooleanField(
        default=False,
        verbose_name='funcionalidade - multi lotes',
        help_text='Liberar funcionalidade de multi lotes'
    )

    feature_raffle = models.BooleanField(
        default=False,
        verbose_name='funcionalidade - sorteios',
        help_text='Liberar funcionalidade de sorteios'
    )
