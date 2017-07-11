# pylint: disable=W5101
"""
Resposta de campos adicionais de formulário de evento.
"""

import json

from django.db import models
from django.utils import six
from jsonfield import JSONField

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
    value = JSONField(verbose_name='valor', null=True, blank=True)

    def save(self, *args, **kwargs):
        self.check_rules()
        super(Answer, self).save(*args, **kwargs)

    def check_rules(self):
        """ Verifica regras de negócio. """

        rule.rule_1_mesma_organizacao(self)
        rule.rule_2_resposta_apenas_se_campo_adicional(self)
        rule.rule_3_resposta_com_tipo_correto(self)

    class Meta:
        verbose_name = 'resposta'
        verbose_name_plural = 'respostas'
        ordering = ['field']
        unique_together = (('subscription', 'field'),)

    def __str__(self):
        return str(self.field)

    def get_display_value(self):
        """ Display para valor do campo. """

        if not self.value:
            return None

        try:
            data = json.loads(self.value)
        except TypeError:
            return None

        if 'output' in data:
            output = data['output']

        elif 'value' in data:
            output = data['value']
        else:
            return None

        if isinstance(output, list):
            output = ', '.join(output)

        elif isinstance(output, dict):
            formatted = []
            for key, value in six.iteritems(output):
                dict_value = str(key) + ': ' + str(value)
                formatted.append(dict_value)

            output = ', '.join(formatted)

        else:
            output = str(output)

        return output

    def get_value(self):
        """ Recupera valor de campo. """

        if not self.value:
            return None

        try:
            data = json.loads(self.value)
        except TypeError:
            return None

        if 'value' in data:
            return data.get('value')

        return None
