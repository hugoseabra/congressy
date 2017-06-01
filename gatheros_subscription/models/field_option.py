# pylint: disable=W5101
"""
Opção de campo de formulário para dar suporte a diversos valores possíveis
para um campo.
"""

from django.db import models

from . import Field
from .rules import field_option as rule


# @TODO valores únicos para a pergunta
class FieldOption(models.Model):
    """ Modelo de opção de campo. """

    field = models.ForeignKey(
        Field,
        on_delete=models.CASCADE,
        verbose_name='campo',
        related_name='options'
    )
    name = models.CharField(max_length=255, verbose_name='rótulo')
    value = models.CharField(
        max_length=255,
        verbose_name='valor',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Opção de Campo'
        verbose_name_plural = 'Opções de Campo'
        ordering = ['field__form__id', 'field__id', 'name']
        unique_together = (('field', 'value'),)

    def save(self, *args, **kwargs):
        self.check_rules()
        super(FieldOption, self).save(*args, **kwargs)

    def check_rules(self):
        """ Verifica regras de negócio. """

        rule.rule_1_somente_campos_com_opcoes(self)

    def __str__(self):
        return '{} [{}] - {} ({})'.format(
            self.name,
            self.value,
            self.field.label,
            self.field.form.event.name
        )
