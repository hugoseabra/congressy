from django import forms
from django.db import models

from core.model import deletable, track_data
from core.util import slugify
from . import Category, Organization, Place
from .rules import event as rule


class TextFieldWithInputText(models.TextField):
    def formfield( self, **kwargs ):
        kwargs.update({"widget": forms.TextInput})
        return super(TextFieldWithInputText, self).formfield(**kwargs)


# @TODO Cores: encontrar as 2 cores (primária e secundária) mais evidentes das imagens e persisti-las
# @TODO gerenciar redirecionamento http em caso de mudança de slug

# @TODO redimensionar banner pequeno para altura e largura corretas - 580 x 422
# @TODO redimensionar banner destaque para altura e largura corretas - 1140 x 500
# @TODO redimensionar banner de topo para altura e largura corretas - 1920 x 900

@track_data('subscription_type')
class Event(models.Model, deletable.DeletableModel):
    RESOURCE_URI = '/api/core/events/'

    SUBSCRIPTION_BY_LOTS = 'by_lots'
    SUBSCRIPTION_SIMPLE = 'simple'
    SUBSCRIPTION_DISABLED = 'disabled'

    SUBSCRIPTION_CHOICES = (
        (SUBSCRIPTION_DISABLED, 'Desativadas'),
        (SUBSCRIPTION_SIMPLE, 'Simples (gratuitas)'),
        (SUBSCRIPTION_BY_LOTS, 'Gerenciar por lotes'),
    )

    name = TextFieldWithInputText(verbose_name='nome')

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

    slug = models.CharField(
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
                  ' rascunhos.')

    class Meta:
        verbose_name = 'evento'
        verbose_name_plural = 'eventos'
        ordering = ('name', 'pk', 'category__name')

    def save( self, *args, **kwargs ):
        self._create_unique_slug()
        self.full_clean()
        super(Event, self).save(*args, **kwargs)

    def clean( self ):
        rule.rule_1_data_inicial_antes_da_data_final(self)
        rule.rule_2_local_deve_ser_da_mesma_organizacao_do_evento(self)

    def __str__( self ):
        return str(self.name)

    def _create_unique_slug( self ):
        self.slug = slugify(model_class=Event, slugify_from=self.name,
                            pk=self.pk)

    def get_period( self ):
        start_date = self.date_start.date()
        end_date = self.date_end.date()
        start_time = self.date_start.time()
        end_time = self.date_end.time()

        if start_date < end_date:
            return 'De ' + self.date_start.strftime(
                '%d/%m/%Y %Hh%M') + ' a ' + self.date_end.strftime(
                '%d/%m/%Y %Hh%M')

        if start_date == end_date:
            return self.date_start.strftime('%d/%m/%Y') \
                   + ' das ' \
                   + start_time.strftime('%Hh%M') \
                   + ' às ' \
                   + end_time.strftime('%Hh%M')
