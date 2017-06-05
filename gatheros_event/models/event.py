# pylint: disable=W5101
"""
Evento é o modelo chave de toda a aplicação: uma estrutura de realização
feita por um organizador de evento, dono de uma organização, e que deseja
apresentar informações ligadas a ela a pessoa que possam se interessar em
participar do evento.
"""
from collections import Counter
from datetime import datetime

from django.db import models
from django.utils.encoding import force_text

from core.model import track_data
from core.util import slugify
from . import Category, Organization, Place
from .rules import event as rule

from .mixins import GatherosModelMixin


# @TODO Cores: encontrar 2 cores (primária e secundária) para hot site
# @TODO gerenciar redirecionamento http em caso de mudança de slug

# @TODO redimensionar banner pequeno para altura e largura corretas - 580 x 422
# @TODO redimensionar banner destaque para alt. e lar. corretas - 1140 x 500
# @TODO redimensionar banner de topo para alt. e larg. corretas - 1920 x 900

# @TODO Excluir imagens banners ao deletar evento.

@track_data('subscription_type', 'date_start', 'date_end')
class Event(models.Model, GatherosModelMixin):
    """Modelo de Evento"""

    RESOURCE_URI = '/api/core/events/'

    SUBSCRIPTION_BY_LOTS = 'by_lots'
    SUBSCRIPTION_SIMPLE = 'simple'
    SUBSCRIPTION_DISABLED = 'disabled'

    SUBSCRIPTION_CHOICES = (
        (SUBSCRIPTION_DISABLED, 'Desativadas'),
        (SUBSCRIPTION_SIMPLE, 'Simples (gratuitas)'),
        (SUBSCRIPTION_BY_LOTS, 'Gerenciar por lotes'),
    )

    EVENT_STATUS_RUNNING = 'running'
    EVENT_STATUS_FINISHED = 'finished'

    STATUSES = (
        (None, 'não-iniciado'),
        (EVENT_STATUS_RUNNING, 'andamento'),
        (EVENT_STATUS_FINISHED, 'finalizado'),
    )

    name = models.CharField(max_length=255, verbose_name='nome')

    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        verbose_name='organização',
        related_name='events'
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        verbose_name='categoria'
    )

    subscription_type = models.CharField(
        max_length=15,
        choices=SUBSCRIPTION_CHOICES,
        default=SUBSCRIPTION_SIMPLE,
        verbose_name='inscrições',
        help_text="Como gostaria de gerenciar as inscrições de seu evento?"
    )

    subscription_offline = models.BooleanField(
        default=False,
        verbose_name='ativar inscrições off-line',
        help_text='Ativar a sincronização para usar off-line no dia do evento.'
    )

    slug = models.SlugField(
        max_length=128,
        unique=True,
        editable=False,
        verbose_name='permalink'
    )

    date_start = models.DateTimeField(verbose_name='data inicial')
    date_end = models.DateTimeField(verbose_name='data final')

    place = models.ForeignKey(
        Place,
        on_delete=models.SET_NULL,
        verbose_name='local',
        blank=True,
        null=True,
        help_text="Deixar em branco se o evento é apenas on-line.",
    )

    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='descrição',
        help_text="Descrição que irá aparecer nos sites de busca e redes"
                  " sociais. Quanto mais detalhada, melhor!"
    )

    banner_small = models.ImageField(
        blank=True,
        null=True,
        verbose_name='banner pequeno',
        help_text="Banner pequeno para apresentação geral (tamanho: 580px"
                  " x 422px)"
    )

    banner_slide = models.ImageField(
        blank=True,
        null=True,
        verbose_name='banner destaque',
        help_text="Banner pequeno para destaque (tamanho: 1140px x 500px)"
    )

    banner_top = models.ImageField(
        blank=True,
        null=True,
        verbose_name='banner topo do site',
        help_text="Banner para o topo do site do evento"
                  " (tamanho: 1920px x 900px)"
    )

    website = models.CharField(max_length=255, null=True, blank=True)
    facebook = models.CharField(max_length=255, null=True, blank=True)
    twitter = models.CharField(max_length=255, null=True, blank=True)
    linkedin = models.CharField(max_length=255, null=True, blank=True)
    skype = models.CharField(max_length=255, null=True, blank=True)
    published = models.BooleanField(
        default=False,
        verbose_name='publicado',
        help_text='Eventos não publicados e com data futura serão considerados'
                  ' rascunhos.'
    )

    class Meta:
        verbose_name = 'evento'
        verbose_name_plural = 'eventos'
        ordering = ('name', 'pk', 'category__name')

        permissions = (
            ("view_lots", "Can view lots"),
            ('add_lot', 'Can add lot'),
        )

    @property
    def limit(self):
        """Limit do evento de acordo com os lotes existentes."""
        limit = 0
        if hasattr(self, 'lots'):
            for lot in self.lots.all():
                if lot.limit:
                    limit += lot.limit

        return limit

    @property
    def percent_completed(self):
        completed = 0.0

        if hasattr(self, 'lots'):
            for lot in self.lots.all():
                completed += lot.percent_completed

            completed = completed / self.lots.count()

        return round(completed, 2)

    @property
    def percent_attended(self):
        attended = 0.0
        if hasattr(self, 'subscriptions'):
            queryset = self.subscriptions
            num = queryset.count()

            if num > 0:
                num_attended = queryset.filter(attended=True).count()
                attended = (num_attended * 100) / num

        return round(attended, 2)

    @property
    def status(self):
        """Status do evento de acordo com suas datas."""
        now = datetime.now()
        if now >= self.date_end:
            return Event.LOT_STATUS_FINISHED

        if self.date_start <= now <= self.date_end:
            return Event.LOT_STATUS_RUNNING

        return None

    def get_status_display(self):
        """ Recupera o status do evento de acordo com a propriedade 'status'"""
        return force_text(
            dict(Event.STATUSES).get(self.status, None),
            strings_only=True
        )

    def save(self, *args, **kwargs):
        self._create_unique_slug()
        self.check_rules()
        super(Event, self).save(*args, **kwargs)

    def check_rules(self):
        """Verifica regras do evento"""
        rule.rule_1_data_inicial_antes_da_data_final(self)
        rule.rule_2_local_deve_ser_da_mesma_organizacao_do_evento(self)
        rule.rule_3_evento_data_final_posterior_atual(self, self._state.adding)
        rule.rule_4_running_published_event_cannot_change_date_start(self)

    def __str__(self):
        return str(self.name)

    def _create_unique_slug(self):
        self.slug = slugify(
            model_class=Event,
            slugify_from=self.name,
            primary_key=self.pk
        )

    def get_period(self):
        """Recupera string de período de evento de acordo com as datas."""
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

    def get_report(self):
        """
        Recupera um dicinário com informaçõse que podem ser utilizadas como
        relatório.
        """
        if not hasattr(self, 'subscriptions'):
            return {}

        def perc(num, num_total):
            if num_total == 0:
                return 0
            return '{0:.2f}%'.format((num * 100) / num_total)

        queryset = self.subscriptions
        total = queryset.count()
        subs = queryset.values(
            'person__pne',
            'person__gender',
            'person__city'
        ).annotate(
            num_pnes=models.Count('person__pne'),
            num_gender=models.Count('person__gender')
        ).order_by()

        men = [
            sub['num_gender'] for sub in subs if sub['person__gender'] == 'M'
        ]
        num_men = sum(men)

        women = [
            sub['num_gender'] for sub in subs if sub['person__gender'] == 'F'
        ]
        num_women = sum(women)

        pnes = [sub['num_pnes'] for sub in subs if sub['person__pne'] is True]
        num_pnes = sum(pnes)

        cities = [sub['person__city'] for sub in subs]
        num_cities = len(Counter(cities))

        return {
            'num_men': '{} ({})'.format(num_men, perc(num_men, total)),
            'num_women': '{} ({})'.format(num_women, perc(num_women, total)),
            'num_pnes': '{} ({})'.format(num_pnes, perc(num_pnes, total)),
            'num_cities': num_cities,
        }
