# pylint: disable=W5101
"""
Opção de campo de formulário para dar suporte a diversos valores possíveis
para um campo.
"""

from django.db import models

from core.util import model_field_slugify
from . import AbstractDefaultFieldOption, Field
from .rules import field_option as rule


# @TODO valores únicos para a pergunta
class FieldOption(AbstractDefaultFieldOption):
    """ Modelo de opção de campo. """

    field = models.ForeignKey(
        Field,
        on_delete=models.CASCADE,
        verbose_name='campo',
        related_name='options'
    )

    class Meta:
        verbose_name = 'Opção de Campo'
        verbose_name_plural = 'Opções de Campo'
        ordering = ['field__id', 'name']
        unique_together = (('field', 'value'),)

    def save(self, *args, **kwargs):
        default = self.field.form_default_field is True
        if default and not self.value or not default:
            self.value = model_field_slugify(
                model_class=self.__class__,
                instance=self,
                string=self.name,
                filter_keys={'field': self.field},
                slug_field='value'
            )

        self.check_rules()
        super(FieldOption, self).save(*args, **kwargs)

    def check_rules(self):
        """ Verifica regras de negócio. """

        rule.rule_1_somente_campos_com_opcoes(self)

    def __str__(self):
        return '{} [{}] - {}'.format(
            self.name,
            self.value,
            self.field.label
        )
