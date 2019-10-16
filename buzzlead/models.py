# pylint: disable=W5101
from decimal import Decimal

from django.db import models

from base.models import EntityMixin
from core.model import track_data
from gatheros_event.models import Event


@track_data('event', 'campaign_id', 'campaign_owner_token')
class BuzzLeadCampaign(models.Model, EntityMixin):
    """ Modelo de campanha da buzzlead """

    class Meta:
        verbose_name = 'campanha buzzlead'
        verbose_name_plural = 'campanhas buzzlead'
        ordering = ('event__name', 'event__date_start', 'pk')

    event = models.OneToOneField(
        'gatheros_event.Event',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='buzzlead_campaign',
        verbose_name='evento'
    )

    campaign_id = models.CharField(
        max_length=6,
        verbose_name='ID da campanha',
        null=False,
        blank=False,
    )

    campaign_owner_token = models.CharField(
        max_length=110,
        verbose_name='API Token do assinante',
        null=False,
        blank=False,
    )

    signature_price = models.DecimalField(
        default=Decimal(0.00),
        verbose_name='valor da assinatura',
        decimal_places=10,
        max_digits=25,
        null=False,
        help_text='Valor da assinatura de uso dos serviços da Buzzlead'
    )

    signature_email = models.CharField(
        max_length=110,
        verbose_name='E-mail do assinante',
        null=False,
        blank=False,
    )

    congressy_percent = models.DecimalField(
        max_length=5,
        verbose_name='percentual congressy',
        decimal_places=10,
        max_digits=25,
        help_text="Valor percentual da congressy pago pela integração.",
        null=False,
        blank=False,
    )

    active = models.BooleanField(default=False, verbose_name='ativo')
    paid = models.BooleanField(default=False, verbose_name='pago')

    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name='criado em')
    modified = models.DateTimeField(auto_now=True,
                                    verbose_name='modificado em')

    @property
    def created_display(self):
        return self.created.strftime('%d/%m/%Y %Hh%m')

    @property
    def enabled(self):
        return self.active is True and self.paid is True and self.campaign_id

    def __str__(self):
        return self.event.name + ' - ' + self.campaign_id
