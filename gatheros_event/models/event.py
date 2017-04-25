from django import forms
from django.core.exceptions import ValidationError
from django.db import models

from . import Category, Organization, Place
from ..signals import track_data


class TextFieldWithInputText(models.TextField):
    def formfield(self, **kwargs):
        kwargs.update({"widget": forms.TextInput})
        return super(TextFieldWithInputText, self).formfield(**kwargs)


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
    organization = models.ForeignKey(Organization, verbose_name='organização')
    category = models.ForeignKey(Category, verbose_name='categoria')

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
        if self.date_end < self.date_start:
            raise ValidationError({'date_start': ['Data inicial deve anterior a data final']})

        if self.place and self.place.organization != self.organization:
            raise ValidationError({'place': ['Local do evento não pertence a sua organização']})

    def __str__(self):
        return str(self.name)
