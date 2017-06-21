# pylint: disable=C0103
"""Regras de Negócios para opção de campo."""

from django.core.exceptions import ValidationError


def rule_1_somente_campos_com_opcoes(option):
    """
    Só pode-se relacionar field_option a campos com tipos corretos que aceitam
    opções.
    """
    if not option.field.with_options:
        raise ValidationError({'field': [
            'O campo `{}` não aceita opções.'.format(option.field.label)
        ]})
