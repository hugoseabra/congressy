# pylint: disable=W5101
"""
Lotes são importantes para agrupar as inscrições de um evento, para separar
os critérios de inscrições: se gratuitas, se limitadas, se privados, etc.
"""

import uuid
import locale
from datetime import datetime, timedelta

from django.db import models
from django.utils.encoding import force_text

from gatheros_event.models import Event
from gatheros_event.models.mixins import GatherosModelMixin
from .rules import lot as rule


class LotManager(models.Manager):
    """ Manager - Gerenciador de lote. """

    def num_lots(self, lot):
        """ Resgata números em um evento. """
        return self.filter(event=lot.event_id).count()

    def get_next_lot_number(self, event):
        """ Resgata número do próximo lote a ser registrado em um evento. """
        return self.filter(event=event).count() + 1

    def generate_promo_code(self):
        """ Gera código promocional para o lote. """
        while True:
            code = str(uuid.uuid4()).split('-')[0].upper()
            try:
                self.get(promo_code=code)
            except Lot.DoesNotExist:
                return code

    def generate_exhibition_code(self):
        """ Gera código de exibição para o lote. """
        while True:
            code = str(uuid.uuid4()).split('-')[0].upper()
            try:
                self.get(exhibition_code=code)
            except Lot.DoesNotExist:
                return code


class Lot(models.Model, GatherosModelMixin):
    """ Modelo de Lote """

    INTERNAL_DEFAULT_NAME = 'default'

    DISCOUNT_TYPE_PERCENT = 'percent'
    DISCOUNT_TYPE_MONEY = 'money'

    INSTALLMENTS = [('INSTALLMENT_' + str(i), str(i)) for i in range(2,10)]

    DISCOUNT_TYPE = (
        (DISCOUNT_TYPE_PERCENT, '%'),
        (DISCOUNT_TYPE_MONEY, 'R$'),
    )

    LOT_LIMIT_UNLIMIED = 'ilimitados'

    LOT_STATUS_NOT_STARTED = 'not-started'
    LOT_STATUS_RUNNING = 'running'
    LOT_STATUS_FINISHED = 'finished'

    STATUSES = (
        (None, 'não-iniciado'),
        (LOT_STATUS_NOT_STARTED, 'não-iniciado'),
        (LOT_STATUS_RUNNING, 'andamento'),
        (LOT_STATUS_FINISHED, 'finalizado'),
    )

    name = models.CharField(
        max_length=255,
        verbose_name='nome'
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name='evento',
        related_name='lots'
    )
    date_start = models.DateTimeField(verbose_name='data inicial')
    date_end = models.DateTimeField(
        verbose_name='data final',
        null=True,
        blank=True
    )
    limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='vaga(s)',
        help_text="Em caso de 0, as inscrições serão ilimitadas."
    )
    price = models.DecimalField(
        max_digits=8,
        null=True,
        blank=True,
        decimal_places=2,
        verbose_name='valor'
    )
    tax = models.DecimalField(
        max_digits=5,
        null=True, blank=True,
        decimal_places=2,
        verbose_name='taxa'
    )
    discount_type = models.CharField(
        max_length=15,
        choices=DISCOUNT_TYPE,
        default='percent',
        verbose_name='tipo de desconto',
        null=True,
        blank=True
    )
    discount = models.DecimalField(
        max_digits=8,
        null=True,
        blank=True,
        decimal_places=2,
        verbose_name='desconto'
    )
    promo_code = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        verbose_name='código promocional'
    )
    transfer_tax = models.BooleanField(
        default=False,
        verbose_name='repassar taxa ao participante',
        help_text="Repasse a taxa para o participante e receba o valor integral do ingresso."
    )

    allow_installments = models.BooleanField(
        default=False,
        verbose_name='parcelamento',
        help_text="Permitir parcelamento do valor do ingresso."
    )

    transfer_interest_rate = models.BooleanField(
        default=False,
        verbose_name='repassar juros de parcelamento ao participante',
        help_text="Repasse os juros das parcelas para o participante e receba o valor integral da parcela."
    )

    installments = models.CharField(
        max_length=15,
        choices=INSTALLMENTS,
        verbose_name='parcelas',
        null=True,
        blank=True
    )

    private = models.BooleanField(
        default=False,
        verbose_name='privado',
        help_text="Se deseja que somente pessoas com código de exibição possam"
                  " se inscrever nesse lote."
    )

    internal = models.BooleanField(
        default=False,
        verbose_name='interno'
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name='criado em')

    exhibition_code = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        verbose_name='código de exibição',
        help_text="Código foi gerado, porém você pode personaliza-lo como"
                  " quiser."
    )

    objects = LotManager()

    class Meta:
        verbose_name = 'lote'
        verbose_name_plural = 'lotes'
        ordering = ['date_start', 'date_end', 'pk', 'name']
        unique_together = (("name", "event"),)

    @property
    def percent_completed(self):
        """ Resgata percentual de vagas preenchidas no lote. """
        completed = 0.00
        if self.limit:
            completed = ((self.subscriptions.count() * 100) / self.limit)

        return round(completed, 2)

    @property
    def percent_attended(self):
        """ Resgata percentual de inscritos que compareceram no evento. """
        queryset = self.subscriptions
        num_subs = queryset.count()
        if num_subs == 0:
            return 0

        attended = queryset.filter(attended=True).count()
        return round((attended * 100)/num_subs, 2)

    @property
    def display_publicly(self):
        """ Exibição pública de infomações do lote. """

        if self.price is not None:
            display = '{} - R$ {} ({} vagas restantes)'.format(
                self.name,
                locale.format(percent='%.2f', value=self.price, grouping=True),
                self.places_remaining
            )

        else:
            display = '{} vagas restantes'.format(self.places_remaining)

        return display

    @property
    def places_remaining(self):
        """ Retorna a quantidade ainda restante de vagas. """
        if not self.limit:
            return self.LOT_LIMIT_UNLIMIED

        num = self.subscriptions.all().count()
        return self.limit - num

    @property
    def status(self):
        """
        Status do lote de acordo com suas datas.
        :return: string
        """
        if self.limit and self.limit > 0:
            queryset = self.subscriptions
            num_subs = queryset.count()

            if num_subs >= self.limit:
                return Lot.LOT_STATUS_FINISHED

        now = datetime.now()
        if now >= self.date_end:
            return Lot.LOT_STATUS_FINISHED

        if self.date_start <= now <= self.date_end:
            return Lot.LOT_STATUS_RUNNING

        return Lot.LOT_STATUS_NOT_STARTED

    def get_status_display(self):
        """
        Recupera nome do status
        :return: string
        """
        return force_text(
            dict(Lot.STATUSES).get(self.status, None),
            strings_only=True
        )

    def save(self, **kwargs):
        """ Salva entidade. """
        self.full_clean()
        self.check_rules()
        super(Lot, self).save(**kwargs)

        rule.rule_10_lote_privado_deve_ter_codigo_promocional(self)

    def clean(self):
        """ Limpa valores dos campos. """
        if self.private and not self.promo_code:
            self.promo_code = Lot.objects.generate_promo_code()

    def check_rules(self):
        """ Verifica regras de negócio. """

        rule.rule_2_mais_de_1_lote_evento_inscricao_simples(self)
        rule.rule_3_evento_inscricao_simples_nao_pode_ter_lot_externo(self)
        rule.rule_4_evento_inscricao_por_lotes_nao_ter_lot_interno(self)
        rule.rule_8_lot_interno_nao_pode_ter_preco(self)
        rule.rule_11_evento_encerrado_nao_pode_ter_novo(
            self,
            self._state.adding
        )

    def __str__(self):
        return '{} - {}'.format(self.event.name, self.name)

    def adjust_unique_lot_date(self, force=False):
        """ Ajusta datas de lote único do evento. """

        """
        Ajusta data de lote quando o evento possui inscrições simples.
        - Data inicial será:
            * Se evento ainda não iniciou, será na data atual
            * Se evento já inicou, 1 dia antes da data inicial do evento
            * Hora sempre iniciando as 8h da manhã
        - Data final será:*
            * 1 minuto antes da data inicial do evento

        :param force: Boolean - Força atualização de datas do lote
        :return: None
        """
        not_simple = self.event.subscription_type != Event.SUBSCRIPTION_SIMPLE
        if force is False and not_simple:
            return
        event = self.event

        now = datetime.now()
        if event.date_start > now:
            date_start = now
        else:
            date_start = event.date_start

        # self.date_start = self.date_start.replace(hour=8, minute=0, second=0)
        # self.date_end = self.event.date_start - timedelta(minutes=1)
        date_end = event.date_start - timedelta(seconds=1)

        self.date_start = date_start
        self.date_end = date_end

    def get_period(self):
        """ Recupera string formatada de periodo do lote, de acordo com suas
        datas, deivamente formatada.
        """

        start_date = self.date_start.date()
        end_date = self.date_end.date()
        start_time = self.date_start.time()
        end_time = self.date_end.time()

        period = ''
        if start_date < end_date:
            period = 'De ' + self.date_start.strftime('%d/%m/%Y %Hh%M')
            period += ' a ' + self.date_end.strftime('%d/%m/%Y %Hh%M')

        if start_date == end_date:
            period = self.date_start.strftime('%d/%m/%Y')
            period += ' das '
            period += start_time.strftime('%Hh%M')
            period += ' às '
            period += end_time.strftime('%Hh%M')

        return period
