from django import forms
from django.db import models

from . import Category, Organization, Place
from gatheros_event.lib.model import track_data
from .rules import event as rule


class TextFieldWithInputText(models.TextField):
    def formfield(self, **kwargs):
        kwargs.update({"widget": forms.TextInput})
        return super(TextFieldWithInputText, self).formfield(**kwargs)


# @TODO Cores: encontrar as 2 cores (primária e secundária) mais evidentes das imagens e persisti-las

# @TODO gerar slug (único) do nome do evento
# @TODO imagens: banner de topo e banner principal

@track_data('subscription_type')
class Event(models.Model):
    RESOURCE_URI = '/api/core/events/'

    SUBSCRIPTION_BY_LOTS = 'by_lots'
    SUBSCRIPTION_SIMPLE = 'simple'
    SUBSCRIPTION_DISABLED = 'disabled'

    SUBSCRIPTION_CHOICES = (
        (SUBSCRIPTION_DISABLED, 'Desativado'),
        (SUBSCRIPTION_SIMPLE, 'Simples'),
        (SUBSCRIPTION_BY_LOTS, 'Por lotes'),
    )

    name = TextFieldWithInputText(verbose_name='nome')
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, verbose_name='organização',
                                     related_name='events')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='categoria')

    subscription_type = models.CharField(max_length=15, choices=SUBSCRIPTION_CHOICES, default=SUBSCRIPTION_SIMPLE,
                                         verbose_name='inscrições')
    subscription_online = models.BooleanField(default=True, verbose_name='ativar inscrições on-line')
    subscription_offline = models.BooleanField(default=False, verbose_name='ativar inscrições off-line',
                                               help_text='Ativa a sincronização para secretaria')

    date_start = models.DateTimeField(verbose_name='data inicial')
    date_end = models.DateTimeField(verbose_name='data final')

    place = models.ForeignKey(Place, verbose_name='local', blank=True, null=True)
    description = models.TextField(null=True, blank=True, verbose_name='descrição')

    website = models.CharField(max_length=255, null=True, blank=True)
    facebook = models.CharField(max_length=255, null=True, blank=True)
    twitter = models.CharField(max_length=255, null=True, blank=True)
    linkedin = models.CharField(max_length=255, null=True, blank=True)
    skype = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'evento'
        verbose_name_plural = 'eventos'
        ordering = ('name', 'pk', 'category__name')

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Event, self).save(*args, **kwargs)

    def clean(self):
        rule.rule_1_data_inicial_antes_da_data_final(self)
        rule.rule_2_local_deve_ser_da_mesma_organizacao_do_evento(self)

    def __str__(self):
        return str(self.name)
