# pylint: disable=W5101
"""
Inscrições de pessoas em eventos.
"""

import uuid
from datetime import datetime

from django.db import models
from django.db.models import Max

from gatheros_event.models import Event, Person
from . import Lot
from .rules import subscription as rule


class SubscriptionManager(models.Manager):
    """ Gerenciador de inscrição - Manager"""

    def next_count(self, lot):
        count_max = self.filter(lot=lot).aggregate(Max('count'))
        if count_max['count__max']:
            return count_max['count__max'] + 1
        else:
            return 1

    def generate_code(self, event):
        while True:
            code = str(uuid.uuid4()).split('-')[0].upper()
            try:
                self.get(event=event, code=code)
            except Subscription.DoesNotExist:
                return code


# @TODO - verificar se evento irá emitir certificado. Se sim, exigir CPF
# @TODO Acrescentar campo boolean "PNE"

class Subscription(models.Model):
    """ Modelo de inscrição """

    DEVICE_ORIGIN_WEB = 'web'
    DEVICE_ORIGIN_OFFLINE = 'offline'

    DEVICE_ORIGINS = (
        (DEVICE_ORIGIN_WEB, 'WEB'),
        (DEVICE_ORIGIN_OFFLINE, 'Sincronização Off-line'),
    )

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        primary_key=True
    )
    lot = models.ForeignKey(
        Lot,
        verbose_name='lote',
        related_name='subscriptions',
        on_delete=models.PROTECT
    )
    event = models.ForeignKey(
        Event,
        verbose_name='evento',
        related_name='subscriptions',
        blank=True,
        editable=False
    )
    person = models.ForeignKey(
        Person,
        verbose_name='pessoa',
        on_delete=models.PROTECT,
        related_name='subscriptions'
    )
    origin = models.CharField(
        max_length=15,
        choices=DEVICE_ORIGINS,
        default='web',
        verbose_name='origem'
    )
    created_by = models.PositiveIntegerField(verbose_name='criado por')

    attended = models.BooleanField(
        default=False,
        verbose_name='compareceu'
    )
    code = models.CharField(
        max_length=15,
        blank=True,
        verbose_name='código'
    )
    count = models.IntegerField(
        default=None,
        blank=True,
        verbose_name='num. inscrição'
    )

    attended_on = models.DateTimeField(
        verbose_name='confirmado em',
        null=True,
        blank=True
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='criado em'
    )
    modified = models.DateTimeField(
        auto_now_add=True,
        verbose_name='modificado em'
    )
    synchronized = models.BooleanField(default=False)

    objects = SubscriptionManager()

    class Meta:
        verbose_name = 'Inscrição'
        verbose_name_plural = 'Inscrições'
        ordering = ['person', 'event']
        unique_together = (
            ("person", "event"),
            ("lot", "count"),
            ("event", "code"),
        )

    def __str__(self):
        return '{} - {}'.format(self.person.name, self.event.name)

    def save(self, *args, **kwargs):
        self.full_clean()
        self.check_rules()
        super(Subscription, self).save(*args, **kwargs)

    def clean(self):
        self.event = self.lot.event

    def check_rules(self):
        """ Verifica regras de negócios de inscrição """

        rule.rule_1_limite_lote_excedido(self)

        # RULE 2 - rule.rule_2_codigo_inscricao_deve_ser_gerado
        if not self.code:
            self.code = Subscription.objects.generate_code(self.event)

        # RULE 3 - rule.test_rule_3_numero_inscricao_gerado
        if not self.count:
            self.count = Subscription.objects.next_count(self.lot)

        # RULE 4 - test_rule_4_inscricao_confirmada_com_data_confirmacao
        if self.attended is True:
            self.attended_on = datetime.now()
        else:
            self.attended_on = None

        rule.rule_5_inscricao_apos_data_final_lote(self, self._state.adding)
        rule.rule_6_inscricao_apos_data_final_evento(self, self._state.adding)

    def get_count_display(self):
        """ Recupera display de formatação de número de inscrição. """

        if not self.count:
            return '--'
        return '{0:03d}'.format(self.count)
