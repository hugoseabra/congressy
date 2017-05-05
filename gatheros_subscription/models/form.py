from django.db import models

from gatheros_event.models import Event
from .rules import form as rule


# @TODO Campos pre-definidos cadastrados a parte e inseridos na criação de novo form
class Form(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, verbose_name='evento', related_name='form')
    created = models.DateTimeField(auto_now_add=True, verbose_name='criado em')

    class Meta:
        verbose_name = 'formulário de evento'
        verbose_name_plural = 'formulários de eventos'
        ordering = ['event']

    def save( self, *args, **kwargs ):
        self.full_clean()
        super(Form, self).save(*args, **kwargs)

    def __str__( self ):
        return self.event.name

    def clean( self ):
        rule.rule_1_form_em_event_inscricao_desativada(self)

    @property
    def get_additional_fields( self ):
        return self.fields.filter(form_default_field=False)

    @property
    def has_additional_fields( self ):
        return self.get_additional_fields.count() > 0
