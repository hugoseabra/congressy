import uuid
from datetime import datetime, timedelta
from django.utils.encoding import force_text

from django.db import models

from gatheros_event.models import Event
from .rules import lot as rule


class LotManager(models.Manager):
    def generate_promo_code(self):
        while True:
            code = str(uuid.uuid4()).split('-')[0].upper()
            try:
                self.get(promo_code=code)
            except Lot.DoesNotExist:
                return code


class Lot(models.Model):
    INTERNAL_DEFAULT_NAME = 'default'

    DISCOUNT_TYPE = (
        ('percent', '%'),
        ('money', 'R$'),
    )

    LOT_STATUS_RUNNING = 'running'
    LOT_STATUS_FINISHED = 'finished'

    STATUSES = (
        (None, 'não-iniciado'),
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
        verbose_name='vaga(s)'
    )
    price = models.DecimalField(
        max_digits=8,
        null=True,
        blank=True,
        decimal_places=2,
        verbose_name='preco'
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
        verbose_name='trasferir taxa para participante'
    )
    private = models.BooleanField(
        default=False,
        verbose_name='privado',
        help_text="Não estará explícito para o participante no site do evento"
    )

    internal = models.BooleanField(
        default=False,
        verbose_name='gerado internamente'
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name='criado em')

    objects = LotManager()

    class Meta:
        verbose_name = 'lote'
        verbose_name_plural = 'lotes'
        ordering = ['pk', 'name', 'event']
        unique_together = (("name", "event"),)

    @property
    def percent_completed(self):
        if not self.limit:
            return None

        completed = ((self.subscriptions.count() * 100) / self.limit)
        return '{0:.2f}%'.format(round(completed, 2))

    @property
    def status(self):
        now = datetime.now()
        if now >= self.date_end:
            return Lot.LOT_STATUS_FINISHED

        if self.date_start <= now <= self.date_end:
            return Lot.LOT_STATUS_RUNNING

        return None

    def get_status_display(self):
        return force_text(
            dict(Lot.STATUSES).get(self.status, None),
            strings_only=True
        )

    def save(self, **kwargs):
        self.full_clean()
        self.check_rules()
        super(Lot, self).save(**kwargs)

        rule.rule_10_lote_privado_deve_ter_codigo_promocional(self)

    def clean(self):
        if not self.date_end:
            self.date_end = self.event.date_start - timedelta(seconds=1)

        if self.private and not self.promo_code:
            self.promo_code = Lot.objects.generate_promo_code()

    def check_rules(self):
        rule.rule_1_event_inscricao_desativada(self)
        rule.rule_2_mais_de_1_lote_evento_inscricao_simples(self)
        rule.rule_3_evento_inscricao_simples_nao_pode_ter_lot_externo(self)
        rule.rule_4_evento_inscricao_por_lotes_nao_ter_lot_interno(self)
        rule.rule_5_data_inicial_antes_data_final(self)
        rule.rule_6_data_inicial_antes_data_inicial_evento(self)
        rule.rule_7_data_final_antes_data_inicial_evento(self)
        rule.rule_8_lot_interno_nao_pode_ter_preco(self)
        rule.rule_9_lote_pago_deve_ter_limite(self)
        rule.rule_11_evento_encerrado_nao_pode_ter_novo(
            self,
            self._state.adding
        )

    def __str__(self):
        return '{} - {}'.format(self.event.name, self.name)
