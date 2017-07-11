# pylint: disable=C0103
"""Regras de Negócios para formulário de evento."""

from django.db import IntegrityError

from gatheros_event.models import Event
from .. import DefaultField


def rule_1_form_em_event_inscricao_desativada(form):
    """
    Evento com inscrição desativada não possui formulário.
    """
    event = form.event
    if event.subscription_type == Event.SUBSCRIPTION_DISABLED:
        raise IntegrityError(
            'O evento {} está com as inscrições desativadas e não pode ter'
            ' formulários.'.format(event.name)
        )


def rule_2_form_possui_todos_campos_padrao(form):
    """
    Garantia de que todas as inscrição terão as informações exigidas pelo
    sistema.
    """
    existing_fields = [
        f.name for f in form.fields.filter(form_default_field=True)
    ]

    missing_fields = []
    for default_field in DefaultField.objects.all():
        if default_field.name not in existing_fields:
            missing_fields.append(default_field.label)

    if missing_fields:
        raise IntegrityError(
            'O evento "{}" não possui o(s) seguinte(s) campo(s)'
            ' padrão: {}'.format(form.event.name, ', '.join(missing_fields))
        )
