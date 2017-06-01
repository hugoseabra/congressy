# pylint: disable=W5101
"""
Resposta de campos adicionais de formulário de evento.
"""

import json

from django.db import models

from gatheros_subscription.models.rules import answer as rule
from . import Field, Subscription


class Answer(models.Model):
    """ Modelo de resposta de campo de formulário."""

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        verbose_name='inscrição',
        related_name='answers'
    )
    field = models.ForeignKey(
        Field,
        on_delete=models.CASCADE,
        verbose_name='campo',
        related_name='answers'
    )
    value = models.TextField(verbose_name='valor', null=True, blank=True)

    def save(self, *args, **kwargs):
        self.check_rules()
        super(Answer, self).save(*args, **kwargs)

    def check_rules(self):
        """ Verifica regras de negócio. """

        rule.rule_1_campo_inscricao_formulario_mesmo_evento(self)
        rule.rule_2_resposta_apenas_se_campo_adicional(self)
        rule.rule_3_resposta_com_tipo_correto(self)

    class Meta:
        verbose_name = 'resposta'
        verbose_name_plural = 'respostas'
        ordering = ['field']
        unique_together = (('subscription', 'field'),)

    def __str__(self):
        return '{} - {}'.format(self.field, self.value)

    def get_display_value(self):
        """ Display para valor do campo. """

        if not self.value:
            return None

        data = json.loads(self.value)

        result = ''
        if 'display' in data:
            result += data.get('display') + ': '

        value = self.get_value()

        if isinstance(value, list):
            result += ', '.join(value)
        else:
            result += str(value)

        return result

    def get_value(self):
        """ Recupera valor de campo. """

        if not self.value:
            return None

        data = json.loads(self.value)
        if 'value' in data:
            return data.get('value')

        return None
