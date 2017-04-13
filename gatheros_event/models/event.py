from django import forms
from django.db import models
from . import Organization, Category, Place


class TextFieldWithInputText(models.TextField):
    def formfield(self, **kwargs):
        kwargs.update({"widget": forms.TextInput})
        return super(TextFieldWithInputText, self).formfield(**kwargs)


class Event(models.Model):
    RESOURCE_URI = '/api/core/events/'

    SUBSCRIPTION_CHOICES = (
        ('on', 'On-line'),
        ('disabled', 'Desativado'),
    )

    name = TextFieldWithInputText(verbose_name='nome')
    organization = models.ForeignKey(Organization, verbose_name='organização')
    category = models.ForeignKey(Category, verbose_name='categoria')

    subscription_type = models.CharField(max_length=15, choices=SUBSCRIPTION_CHOICES, default='on',
                                         verbose_name='inscrições')

    date_start = models.DateTimeField(verbose_name='data inicial')
    date_end = models.DateTimeField(verbose_name='data final')

    place = models.ForeignKey(Place, verbose_name='endereço', blank=True, null=True)
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

    def __str__(self):
        return str(self.name)
