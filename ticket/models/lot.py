from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.db import models

from base.models import EntityMixin
from core.util.date import DateTimeRange
from gatheros_event.models.mixins import GatherosModelMixin


class Lot(GatherosModelMixin, EntityMixin, models.Model):
    class Meta:
        verbose_name = "lote de ingressos"
        verbose_name_plural = "lotes de ingressos"
        unique_together = (
            ('ticket', 'date_start', 'date_end',),
        )

    ticket = models.ForeignKey(
        'ticket.Ticket',
        on_delete=models.CASCADE,
        verbose_name='ingresso de participante',
        related_name='lots',
        # Making field required
        blank=False,
        null=False,
    )

    date_start = models.DateTimeField(
        verbose_name='data/hora inicial',
        # Making field required
        blank=False,
        null=False,
    )

    date_end = models.DateTimeField(
        verbose_name='data/hora final',
        # Making field required
        blank=False,
        null=False,
    )

    price = models.DecimalField(
        verbose_name="preço",
        max_digits=8,
        decimal_places=2,
        default=Decimal(0.00),
        # Making field optional
        blank=True,
        null=True,
    )

    limit = models.PositiveIntegerField(
        verbose_name="limite de inscrições",
        # Making field optional
        blank=True,
        null=True,
        help_text="numero total de inscrições para que o lote"
    )

    num_subs = models.PositiveIntegerField(
        verbose_name="numero de inscrições",
        # Making field optional
        blank=True,
        default=0,
        null=True,
        editable=False,
        help_text="controle interno para contagem de inscrições",
    )

    created = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name='criado em'
    )

    modified = models.DateTimeField(
        auto_now=True,
        editable=False,
        verbose_name='modificado em'
    )

    def __init__(self, *args, **kwargs):
        self._event = None
        super().__init__(*args, **kwargs)

    @property
    def event(self):
        if not self._event:
            self._event = self.ticket.event

        return self._event

    @property
    def name(self):
        return self.ticket.name

    @property
    def is_full(self):
        if not self.limit:
            return False

        return self.num_subs >= self.limit

    @property
    def not_started(self):
        now = datetime.now()
        return now < self.date_start

    @property
    def finished(self):
        now = datetime.now()
        return now >= self.date_end

    @property
    def running(self):
        now = datetime.now()
        dates_range = DateTimeRange(start=self.date_start, stop=self.date_end)
        return now in dates_range

    @property
    def subscribable(self):
        return self.running is True \
               and self.is_full is True \
               and self.ticket.active is True \
               and self.ticket.is_full is True

    def update_lot_num_subs(self):
        """
           Número de inscrições em num_subs deve ser controlado e
           centralizado e deve ser usados apenas por signal como controle
           interno
        """

        self.num_subs = self.subscriptions.all_completed().count()
        self.save()

        return self

    def get_subscriber_price(self):
        """
        Resgata o valor calculado do preço do lote de acordo com as regras
        da Congressy.
        """
        if not self.price:
            return Decimal(0.00)

        if self.event.transfer_tax is False:
            return round(self.price, 2)

        minimum = Decimal(settings.CONGRESSY_MINIMUM_AMOUNT)
        congressy_plan_percent = \
            Decimal(self.event.congressy_percent) / 100

        congressy_amount = self.price * congressy_plan_percent
        if congressy_amount < minimum:
            congressy_amount = minimum

        return round(self.price + congressy_amount, 2)