from django.db import models
from django.forms.fields import BooleanField

from gatheros_event.models import Event


class Form(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, verbose_name='evento', related_name='form')
    created = models.DateTimeField(auto_now_add=True, verbose_name='criado em')

    class Meta:
        verbose_name = 'formulário de evento'
        verbose_name_plural = 'formulários de eventos'
        ordering = ['event']

    def __str__(self):
        return self.event.name

    @property
    def additional_fields(self):
        return self.fields.filter(form_default_field=False)

    @property
    def has_additional_fields(self):
        return self.additional_fields.count() > 0
