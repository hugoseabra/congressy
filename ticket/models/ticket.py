import uuid
from datetime import datetime
from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.formats import localize

from base.models import EntityMixin
from gatheros_event.models.mixins import GatherosModelMixin


class TicketManager(models.Manager):
    """ Manager - Gerenciador de lote. """

    def generate_exhibition_code(self):
        """ Gera código de exibição para o lote. """
        while True:
            code = str(uuid.uuid4()).split('-')[0].upper()
            try:
                self.get(exhibition_code=code)
            except ObjectDoesNotExist:
                return code


class Ticket(GatherosModelMixin, EntityMixin, models.Model):
    NOT_STARTED_STATUS = 'not_started'
    RUNNING_STATUS = 'running'
    ENDED_STATUS = 'ended'

    STATUSES = (
        (NOT_STARTED_STATUS, 'Não iniciado'),
        (RUNNING_STATUS, 'Em andamento'),
        (ENDED_STATUS, 'Encerrado'),
    )

    class Meta:
        verbose_name = 'ingresso'
        verbose_name_plural = 'ingressos'

    objects = TicketManager()

    event = models.ForeignKey(
        'gatheros_event.Event',
        on_delete=models.CASCADE,
        verbose_name='evento',
        related_name="tickets",
        # Making field required
        blank=False,
        null=False,
    )

    event_survey = models.ForeignKey(
        'gatheros_subscription.EventSurvey',
        on_delete=models.SET_NULL,
        verbose_name='formulário personalizado',
        related_name='tickets',
        # Making field optional
        blank=True,
        null=True
    )

    name = models.CharField(
        verbose_name="nome da categoria",
        max_length=255,
        # Making field required
        blank=False,
        null=False,
    )

    description = models.TextField(
        verbose_name="descrição",
        # Making field optional
        blank=True,
        null=True,
    )

    free_installments = models.PositiveIntegerField(
        verbose_name="absorver juros de parcelamento",
        default=0,
        # Making field optional
        blank=True,
        null=True,
    )

    active = models.BooleanField(
        verbose_name="ativo",
        default=True,
        # Making field required
        blank=False,
        null=False,
    )

    limit = models.PositiveIntegerField(
        verbose_name="vagas",
        # Making field optional
        blank=True,
        null=True,
    )

    num_subs = models.PositiveIntegerField(
        verbose_name="numero de inscrições",
        # Making field optional
        blank=True,
        null=True,
        default=0,
        help_text='controle interno para contagem de inscrições',
        editable=False,
    )

    private = models.NullBooleanField(
        verbose_name="privado",
        default=False,
        # Making field required
        blank=False,
        null=False,
    )

    exhibition_code = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        verbose_name='código de exibição',
        unique=True,
    )

    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='criado em',
        editable=False,
    )

    modified = models.DateTimeField(
        auto_now=True,
        verbose_name='modificado em',
        editable=False,
    )

    def __str__(self):
        return self.name

    def __repr__(self):
        return '{} - ID: {}'.format(
            self.name, str(self.pk)
        )

    def __init__(self, *args, **kwargs):
        self._current_lot = None
        super().__init__(*args, **kwargs)

    @property
    def display_name_and_price(self):
        return '{}{}'.format(
            self.name,
            ' - R$ {}'.format(
                localize(self.get_subscriber_price())
            ) if self.price else '',
        )

    @property
    def current_lot(self):
        """
            Resgatar o lote vigente no ingresso, caso possua.
        """

        if self._current_lot:
            return self._current_lot

        found_lots = list()

        for lot in self.lots.all():
            if lot.running is True:
                found_lots.append(lot)

        assert len(found_lots) <= 1, \
            '{} lotes ativos neste momento.'.format(len(found_lots))

        if found_lots:
            self._current_lot = found_lots[0]

        return self._current_lot

    @property
    def running(self):
        return self.current_lot is not None

    @property
    def status(self):
        if self.running is True:
            return self.RUNNING_STATUS

        now = datetime.now()

        if self.lots.filter(date_start__gte=now).count() > 0:
            return self.NOT_STARTED_STATUS

        return self.ENDED_STATUS

    @property
    def is_full(self):
        if not self.limit:
            return False

        return self.num_subs >= self.limit

    @property
    def subscribable(self):
        current_lot = self.current_lot

        if current_lot is None:
            return False

        return current_lot.subscribable is True

    @property
    def price(self):
        return self.current_lot.price if self.current_lot else 0

    @property
    def get_period(self):
        return self.current_lot.get_period() if self.current_lot else None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.private and not self.exhibition_code:
            self.exhibition_code = Ticket.objects.generate_exhibition_code()

    def update_audience_category_num_subs(self):
        """
        Número de inscrições em num_subs deve ser controlado e centralizado por
        signal como controle interno
        """

        counter = 0

        for lot in self.lots.all():
            counter += lot.subscriptions.all_completed().count()

        self.num_subs = counter
        self.save()

        return self

    def get_subscriber_price(self):
        """
        Resgata o valor calculado do preço do lote de acordo com as regras
        da Congressy.
        """
        if not self.current_lot:
            return Decimal(0.00)

        return self.current_lot.get_subscriber_price()
