# pylint: disable=W5101
"""
Formulário de evento, utilizado para captação de informações de pessoas
através de suas inscrições.
"""

from django.db import models

from gatheros_event.models import Event
from .rules import form as rule


class Form(models.Model):
    """ Modelo de Formulário de evento. """

    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        verbose_name='evento',
        related_name='form'
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name='criado em')

    class Meta:
        verbose_name = 'formulário de evento'
        verbose_name_plural = 'formulários de eventos'
        ordering = ['event']

        permissions = (
            ("can_add_field", "Can add field"),
        )

    def save(self, *args, **kwargs):
        self.check_rules()
        super(Form, self).save(*args, **kwargs)

    def __str__(self):
        return self.event.name

    def check_rules(self):
        """ Verifica regras de negócio. """

        rule.rule_1_form_em_event_inscricao_desativada(self)

    @property
    def get_additional_fields(self):
        """ Recupera os campos que são adicionais. """

        return self.fields.filter(form_default_field=False)

    @property
    def has_additional_fields(self):
        """ Verifica se há campos adicionais. """

        return self.get_additional_fields.count() > 0
