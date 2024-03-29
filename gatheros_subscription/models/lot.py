# pylint: disable=W5101
"""
Lotes são importantes para agrupar as inscrições de um evento, para separar
os critérios de inscrições: se gratuitas, se limitadas, se privados, etc.
"""

import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import numberformat
from django.utils.encoding import force_text

from base.models import EntityMixin
from core.model import track_data
from gatheros_event.models import Event
from gatheros_event.models.mixins import GatherosModelMixin
from gatheros_subscription.models import LotCategory
from .event_survey import EventSurvey
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


class RunningLots(models.Manager):
    def all_running_lots(self):
        return


@track_data('name', 'category_id', 'date_start', 'date_end', 'limit', 'price',
            'tax', 'transfer_tax', 'allow_installment', 'allow_installments',
            'installment_limit', 'num_install_interest_absortion', 'private',
            'exhibition_code', 'event_id', 'event_survey_id', 'active')
class Lot(models.Model, GatherosModelMixin, EntityMixin):
    """ Modelo de Lote """

    INTERNAL_DEFAULT_NAME = 'default'

    DISCOUNT_TYPE_PERCENT = 'percent'
    DISCOUNT_TYPE_MONEY = 'money'

    INSTALLMENTS = [('INSTALLMENT_' + str(i), str(i)) for i in range(2, 10)]

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
    category = models.ForeignKey(
        LotCategory,
        on_delete=models.CASCADE,
        verbose_name='categoria',
        related_name='lots',
        null=True,
        blank=True,
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
        verbose_name='valor',
        help_text='R$ 10,00 a R$ 30.000,00'
    )
    tax = models.DecimalField(
        max_digits=5,
        null=True,
        blank=True,
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
        blank=True,
        verbose_name='repassar taxa',
        help_text="Repasse a taxa para o participante e receba o valor"
                  " integral do ingresso."
    )
    allow_installment = models.BooleanField(
        default=True,
        blank=True,
        verbose_name='permitir parcelamento',
    )
    installment_limit = models.PositiveIntegerField(
        default=10,
        blank=True,
        verbose_name='parcelas',
        help_text="Número de parcelas permitido."
    )
    num_install_interest_absortion = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        verbose_name='assumir juros de parcelas',
        help_text="Número de parcelas que deseja assumir os juros."
    )
    # @TODO verificar campo repetido: allow_installment e allow_installments
    allow_installments = models.BooleanField(
        default=False,
        verbose_name='parcelamento',
        help_text="Permitir parcelamento do valor do ingresso."
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
        help_text="Personaliza-lo como quiser."
    )

    event_survey = models.ForeignKey(
        EventSurvey,
        on_delete=models.SET_NULL,
        verbose_name='formulario',
        related_name='lots',
        blank=True,
        null=True
    )

    rsvp_restrict = models.BooleanField(
        default=False,
        verbose_name='restrito a associados',
        help_text='Somente associados podem se inscrever neste lote.'
    )

    description = models.CharField(
        max_length=60,
        verbose_name='descrição rápida',
        help_text='Informações adicionais sobre o lote (60 caracteres).',
        null=True,
        blank=True,
    )

    hide_dates = models.BooleanField(
        default=False,
        verbose_name='ocultar datas do lote',
        help_text='Ocultar data inicial e final do lote.'
    )

    active = models.BooleanField(
        default=True,
        verbose_name='ativo',
    )

    objects = LotManager()

    class Meta:
        verbose_name = 'lote'
        verbose_name_plural = 'lotes'
        ordering = ['date_start', 'date_end', 'pk', 'name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._warning_limit = ''

    @property
    def percent_completed(self):
        """ Resgata percentual de vagas preenchidas no lote. """
        completed = 0.00
        if self.limit:
            queryset = self.subscriptions.filter(
                completed=True, test_subscription=False
            ).exclude(
                status='canceled'
            )
            completed = ((queryset.count() * 100) / self.limit)

        return round(completed, 2)

    @property
    def percent_attended(self):
        """ Resgata percentual de inscritos que compareceram no evento. """
        queryset = self.subscriptions.filter(
            completed=True, test_subscription=False
        ).exclude(
            status='canceled'
        )
        if queryset.count() == 0:
            return 0

        attended = queryset.filter(attended=True).count()
        return round((attended * 100) / queryset.count(), 2)

    @property
    def display_publicly(self):
        """ Exibição pública de infomações do lote. """

        if self.price and self.price > 0:
            if self.rsvp_restrict is True:
                content = '{} - R$ {} (para convidados)'
            else:
                content = '{} - R$ {}'

            return content.format(
                self.name,
                numberformat.format(
                    self.get_calculated_price(),
                    decimal_sep=',',
                    thousand_sep='.',
                    grouping=[3, 3, 2],
                    force_grouping=True,
                ),
                self.places_remaining
            )

        if self.rsvp_restrict is True:
            content = '{} (para convidados)'
        else:
            content = '{}'

        return content.format(self.name)

    @property
    def display_price(self):
        """ Exibição pública de infomações do lote. """

        if self.price and self.price > 0:
            return 'R$ {}'.format(
                numberformat.format(
                    self.get_calculated_price(),
                    decimal_sep=',',
                    thousand_sep='.',
                    grouping=[3, 3, 2],
                    force_grouping=True,
                ),
            )

        return 'R$ 0,00'

    @property
    def places_remaining(self):
        """ Retorna a quantidade ainda restante de vagas. """
        if not self.limit:
            return self.LOT_LIMIT_UNLIMIED

        num = self.subscriptions.filter(
            completed=True,
            test_subscription=False
        ).exclude(
            status='canceled',
        ).count()
        return self.limit - num

    @property
    def status(self):
        """
        Status do lote de acordo com suas datas.
        :return: string
        """
        now = datetime.now()
        if now >= self.date_end:
            return Lot.LOT_STATUS_FINISHED

        elif now < self.date_start:
            return Lot.LOT_STATUS_NOT_STARTED

        if self.limit and self.limit > 0:
            limit_remaining = self.places_remaining
            if limit_remaining != self.LOT_LIMIT_UNLIMIED and limit_remaining <= 0:
                return Lot.LOT_STATUS_FINISHED

            num_expected = self.event.expected_subscriptions

            if num_expected and num_expected > 0:
                total_subscriptions_event = self.event.lots.filter(
                    subscriptions__completed=True,
                    subscriptions__test_subscription=False,
                ).exclude(
                    subscriptions__status='canceled'
                ).count()

                if total_subscriptions_event >= num_expected:
                    return Lot.LOT_STATUS_FINISHED

        return Lot.LOT_STATUS_RUNNING

    @property
    def running(self):
        return self.status == Lot.LOT_STATUS_RUNNING

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

    def clean(self):
        """ Limpa valores dos campos. """

        if self.is_new() is False:
            if self.has_changed('event_id') is True:
                raise ValidationError({'event': [
                    'Você não pode editar o evento do lote.'
                ]})

            if self.subscriptions.filter(
                    completed=True,
                    test_subscription=False
            ).exists():
                if self.has_changed('price'):
                    raise ValidationError({'price': [
                        'Preço não pode ser alterado após haverem inscrições'
                        ' no lote.'
                    ]})

                if self.has_changed('tax'):
                    raise ValidationError({'tax': [
                        'Transferência de taxa não pode ser alterada após'
                        ' haverem inscrições no lote.'
                    ]})

        if self.category and self.category.event_id != self.event_id:
            raise ValidationError({'category': [
                'A categoria do lote e o lote não estão no mesmo evento.'
            ]})

    def check_rules(self):
        """ Verifica regras de negócio. """

        if self.private and not self.exhibition_code:
            self.exhibition_code = Lot.objects.generate_exhibition_code()

        rule.rule_2_mais_de_1_lote_evento_inscricao_simples(self)
        rule.rule_3_evento_inscricao_simples_nao_pode_ter_lot_externo(self)
        rule.rule_4_evento_inscricao_por_lotes_nao_ter_lot_interno(self)
        rule.rule_8_lot_interno_nao_pode_ter_preco(self)
        rule.rule_10_lote_privado_deve_ter_codigo_de_exibicao(self)

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

    def get_calculated_price(self):
        """
        Resgata o valor calculado do preço do lote de acordo com as regras
        da Congressy.
        """
        if not self.price:
            return Decimal(0.00)

        if self.transfer_tax is False:
            return round(self.price, 2)

        minimum = Decimal(settings.CONGRESSY_MINIMUM_AMOUNT)
        congressy_plan_percent = \
            Decimal(self.event.congressy_percent) / 100

        congressy_amount = self.price * congressy_plan_percent
        if congressy_amount < minimum:
            congressy_amount = minimum

        return round(self.price + congressy_amount, 2)

    def display_calculated_price(self):
        """
        Resgata o valor calculado do preço do lote de acordo com as regras
        da Congressy.
        """
        price = self.get_calculated_price()

        if not price:
            return 'R$ 0,00'

        return 'R$ {}'.format(
            numberformat.format(
                price,
                decimal_sep=',',
                thousand_sep='.',
                grouping=[3, 3, 2],
                force_grouping=True,
            ),
        )

    def get_liquid_price(self):
        """
        Resgata o valor calculado do preço do lote de acordo com as regras
        da Congressy.
        """
        if not self.price:
            return Decimal(0.00)

        if self.transfer_tax is True:
            return self.price

        minimum = Decimal(settings.CONGRESSY_MINIMUM_AMOUNT)
        congressy_plan_percent = \
            Decimal(self.event.congressy_percent) / 100

        congressy_amount = self.price * congressy_plan_percent
        if congressy_amount < minimum:
            congressy_amount = minimum

        return round(self.price - congressy_amount, 2)

    def get_warning_limit(self) -> str:
        if self._warning_limit:
            return self._warning_limit

        total_subs_event = self.event.expected_subscriptions
        total_subs_lot = self.limit

        if not total_subs_event and not total_subs_lot:
            return self._warning_limit

        perc = None

        if total_subs_lot:
            num_subs_lot = self.subscriptions.count()
            if num_subs_lot > 0:
                perc = (num_subs_lot * 100) / total_subs_lot

        elif total_subs_event:
            num_subs_event = self.event.subscriptions.count()
            if num_subs_event > 0:
                perc = (num_subs_event * 100) / total_subs_event

        if perc and perc > 80:
            self._warning_limit = 'Últimas vagas'

        return self._warning_limit
