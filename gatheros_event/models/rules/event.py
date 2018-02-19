# pylint: disable=C0103
"""Regras de Negócios para Evento."""

from datetime import datetime

from django.core.exceptions import ValidationError


def rule_1_data_inicial_antes_da_data_final(date_start, date_end):
    """
    Data inicial deve ser antes da data final.
    """
    if date_end < date_start:
        raise ValidationError({'date_start': [
            'Data inicial deve ser anterior a data final.'
        ]})
