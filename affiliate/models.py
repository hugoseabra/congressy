"""
    Models of Affiliate entity
"""

from django.conf import settings
from django.db import models

from affiliate import constants, rules
from base.models import EntityMixin
from gatheros_event.models import Person, Event
from payment.models import BankAccount


class Affiliate(EntityMixin, models.Model):
    """
        Pessoa que se afilia a eventos para ganhar comissão de inscrição que
        ele divulgar.
    """

    person = models.OneToOneField(
        Person,
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name='pessoa',
        related_name='affiliate',
    )

    bank_account = models.OneToOneField(
        BankAccount,
        on_delete=models.SET_NULL,
        related_name='affiliate',
        verbose_name='conta bancária',
        blank=True,
        null=True,
    )

    status = models.CharField(
        choices=constants.STATUSES,
        default=constants.ACTIVE,
        max_length=30,
        verbose_name="status",
        blank=True,
        null=True,
    )

    recipient_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.person.name

    class Meta:
        verbose_name = 'Afiliado'
        verbose_name_plural = 'Afiliados'


class Affiliation(EntityMixin, models.Model):
    """
        A afiliação define relação entre o afiliado e o evento, definindo
        um percentual de participante que sempre deve estar sob controle.
    """
    rule_instances = (
        rules.MustProvideMaxPercentAffiliationRule,
        rules.MaxParticipationExceededAffiliationRule,
    )

    # Valor maximo que afiliado a um evento pode participar da comissão por
    # inscrição.
    AFFILIATE_MAX_PERCENTAGE = settings.AFFILIATE_MAX_PERCENTAGE

    affiliate = models.ForeignKey(
        Affiliate,
        on_delete=models.CASCADE,
        verbose_name='afiliado',
        related_name='affiliations',
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name='evento',
        related_name='affiliations',
    )

    percent = models.DecimalField(
        verbose_name='percentual',
        decimal_places=2,
        max_digits=5,
        help_text='Percentual de participação da afiliação.'
    )

    link_whatsapp = models.TextField(
        verbose_name='link WhatsApp',
    )

    link_facebook = models.TextField(
        verbose_name='link Facebok',
    )

    link_twitter = models.TextField(
        verbose_name='link Twitter',
    )

    link_direct = models.TextField(
        verbose_name='link Direto',
    )

    def __str__(self):
        name = '{} - {}'.format(self.event, self.affiliate.person)
        return name + ' ({0:.2f}%)'.format(self.percent)

    class Meta:
        verbose_name = 'Afiliação'
        verbose_name_plural = 'Afiliações'
