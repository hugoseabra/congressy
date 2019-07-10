# pylint: disable=W5101
"""
Inscrições de pessoas em eventos.
"""

import uuid

from django.db import models
from django.db.models import Max
from django.utils.functional import cached_property

from base.models import EntityMixin
from core.model import track_data
from gatheros_event.models import Event, Person
from gatheros_event.models.constants import (
    CONGRESSY_PERCENTS,
    CONGRESSY_PERCENT_10_0,
)
from gatheros_event.models.mixins import GatherosModelMixin
from survey.models import Author
from . import Lot
from .rules import subscription as rule


class SubscriptionManager(models.Manager):
    """ Gerenciador de inscrição - Manager"""

    def next_event_count(self, event):
        """ Resgata próximo número de inscrição. """
        count_max = self.filter(event=event).aggregate(Max('event_count'))
        if count_max['event_count__max']:
            return count_max['event_count__max'] + 1

        return 1

    def next_count(self, lot):
        """ Resgata próximo número de inscrição. """
        count_max = self.filter(lot=lot).aggregate(Max('count'))
        if count_max['count__max']:
            return count_max['count__max'] + 1

        return 1

    def generate_code(self, event):
        """ Gera código de inscrição. """
        while True:
            code = str(uuid.uuid4()).split('-')[0].upper()
            try:
                self.get(event=event, code=code)
            except Subscription.DoesNotExist:
                return code


@track_data('lot_id')
class Subscription(models.Model, EntityMixin, GatherosModelMixin):
    """ Modelo de inscrição """

    DEVICE_ORIGIN_HOTSITE = 'hotsite'
    DEVICE_ORIGIN_MANAGE = 'manage'
    DEVICE_ORIGIN_CSV_IMPORT = 'csv_import'

    DEVICE_ORIGINS = (
        (DEVICE_ORIGIN_HOTSITE, 'Hotsite do evento'),
        (DEVICE_ORIGIN_MANAGE, 'Manage'),
        (DEVICE_ORIGIN_CSV_IMPORT, 'Import via CSV'),
    )

    CONFIRMED_STATUS = 'confirmed'
    CANCELED_STATUS = 'canceled'
    AWAITING_STATUS = 'awaiting'

    STATUSES = (
        (CONFIRMED_STATUS, 'Confirmado'),
        (CANCELED_STATUS, 'Cancelado'),
        (AWAITING_STATUS, 'Pendente'),
    )

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        primary_key=True
    )

    status = models.CharField(
        max_length=15,
        choices=STATUSES,
        default=AWAITING_STATUS,
        verbose_name='status',
    )

    lot = models.ForeignKey(
        Lot,
        verbose_name='lote',
        related_name='subscriptions',
        on_delete=models.PROTECT,
        # @TODO: Remove this field
        null=True,
        blank=True,
    )

    ticket_lot = models.ForeignKey(
        'ticket.Lot',
        verbose_name='lote',
        related_name='subscriptions',
        on_delete=models.CASCADE,
        # @TODO: Make this field required
        null=True,
        blank=True,
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
        related_name='subscriptions',
    )
    origin = models.CharField(
        max_length=15,
        choices=DEVICE_ORIGINS,
        default=DEVICE_ORIGIN_HOTSITE,
        verbose_name='origem'
    )
    created_by = models.PositiveIntegerField(verbose_name='criado por')

    # Needed for compatibility with 1.5.x
    attended = models.BooleanField(
        default=False,
        verbose_name='compareceu'
    )

    code = models.CharField(
        max_length=15,
        blank=True,
        verbose_name='código'
    )
    event_count = models.IntegerField(
        default=1,
        blank=True,
        verbose_name='num. inscrição geral'
    )
    count = models.IntegerField(
        default=None,
        blank=True,
        verbose_name='num. inscrição'
    )

    # Needed for compatibility with 1.5.x
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
    synchronized = models.BooleanField(default=False, editable=False, )

    notified = models.BooleanField(
        default=False,
        editable=False,
        help_text='Participante notificado.'
    )

    congressy_percent = models.CharField(
        max_length=5,
        choices=CONGRESSY_PERCENTS,
        default=CONGRESSY_PERCENT_10_0,
        verbose_name='percentual congressy',
        help_text="Valor percentual da congressy."
    )

    author = models.OneToOneField(
        Author,
        on_delete=models.DO_NOTHING,
        verbose_name='autor de resposta',
        related_name='subscription',
        blank=True,
        null=True,
    )

    completed = models.BooleanField(
        default=False,
        verbose_name='completa',
        help_text='Inscrições que passaram por todo o fluxo de inscrições.',
    )

    test_subscription = models.BooleanField(default=False)

    tag_info = models.CharField(
        max_length=16,
        verbose_name='informação para crachá',
        help_text="Informação customizada para sair no crachá do participante",
        null=True,
        blank=True,
    )

    tag_group = models.CharField(
        max_length=16,
        verbose_name='informação de grupo',
        help_text="Informação de grupo do participante",
        null=True,
        blank=True,
    )

    obs = models.TextField(
        null=True,
        blank=True,
        help_text="Observações Gerais"
    )

    objects = SubscriptionManager()

    class Meta:
        verbose_name = 'Inscrição'
        verbose_name_plural = 'Inscrições'
        ordering = ['person', 'created', 'event']
        unique_together = (
            ("person", "event"),
            ("lot", "count"),
            ("event", "code"),
            # ("event", "event_count"),
        )

    def __str__(self):
        return '{} - {}'.format(self.person.name, self.event.name)

    @property
    def confirmed(self):
        return self.status == Subscription.CONFIRMED_STATUS

    @property
    def free(self):
        return self.lot is not None and not self.lot.price

    def save(self, *args, **kwargs):
        """ Salva entidade. """
        self.check_rules()
        self.congressy_percent = self.event.congressy_percent
        super(Subscription, self).save(*args, **kwargs)

    def clean(self):
        """ Limpa dados dos campos. """
        self.event = self.lot.event

    def check_rules(self):
        """ Verifica regras de negócios de inscrição """

        if self._state.adding or self.has_changed('lot_id'):
            rule.rule_1_limite_lote_excedido(self)

        # RULE 2 - rule.rule_2_codigo_inscricao_deve_ser_gerado
        if not self.code:
            self.code = Subscription.objects.generate_code(self.event)

        # RULE 3 - rule.test_rule_3_numero_inscricao_gerado
        if not self.event_count:
            self.event_count = Subscription.objects.next_event_count(
                self.event
            )

        if not self.count or self.has_changed('lot_id'):
            self.count = Subscription.objects.next_count(self.lot)

        # RULE 4 - test_rule_4_inscricao_confirmada_com_data_confirmacao
        # if self.attended is True:
        #     self.attended_on = datetime.now()
        # else:
        #     self.attended_on = None

        rule.rule_5_inscricao_apos_data_final_lote(self, self._state.adding)
        rule.rule_6_inscricao_apos_data_final_evento(self, self._state.adding)

    def get_event_count_display(self):
        """ Recupera display de formatação de número de inscrição. """

        if not self.event_count:
            return '--'
        return '{0:03d}'.format(self.event_count)

    def get_count_display(self):
        """ Recupera display de formatação de número de inscrição. """

        if not self.count:
            return '--'
        return '{0:03d}'.format(self.count)

    @cached_property
    def accreditation_checkin(self):
        checkins = self.checkins.filter(
            attendance_service__accreditation=True,
            checkout__isnull=True,
        )

        if checkins.count() == 0:
            return None

        return checkins.last()

    @property
    def accredited(self):
        return self.accreditation_checkin is not None

    @property
    def accredited_on(self):
        checkin = self.accreditation_checkin

        if not checkin:
            return None

        return checkin.registration or checkin.created_on
