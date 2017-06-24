# pylint: disable=W5101
"""
Opção de campo de formulário para dar suporte a diversos valores possíveis
para um campo.
"""

from django.db import models

from . import AbstractDefaultFieldOption, DefaultField
from .rules import field_option as rule


# @TODO valores únicos para a pergunta
class DefaultFieldOption(AbstractDefaultFieldOption):
    """ Modelo de opção de campo. """

    field = models.ForeignKey(
        DefaultField,
        on_delete=models.CASCADE,
        verbose_name='campo',
        related_name='options'
    )

    class Meta:
        verbose_name = 'Opção de Campo Padrão'
        verbose_name_plural = 'Opções de Campo Padrão'
        ordering = ['field__id', 'name']
        unique_together = (('field', 'value'),)

    def save(self, *args, **kwargs):
        self.check_rules()
        super(DefaultFieldOption, self).save(*args, **kwargs)

    def check_rules(self):
        """ Verifica regras de negócio. """

        rule.rule_1_somente_campos_com_opcoes(self)

    def __str__(self):
        return '{} [{}] - {}'.format(
            self.name,
            self.value,
            self.field.label,
        )
