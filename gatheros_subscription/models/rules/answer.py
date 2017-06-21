# pylint: disable=C0103
"""Regras de Negócios para Resposta de campo."""

from django.core.exceptions import ValidationError


def rule_1_campo_inscricao_formulario_mesmo_evento(answer):
    """
    Resposta de um campo de formulário de ser de uma inscrição do evento
    correto.
    """
    answer_event = answer.subscription.event
    field_event = answer.field.form.event
    if answer_event != field_event:
        raise ValidationError(
            {'field': ['Campo não pertence ao evento \'{}\'.'.format(
                field_event.name
            )]}
        )


def rule_2_resposta_apenas_se_campo_adicional(answer):
    """
    Resposta de campo deve apenas se campo é não-padrão, ou seja, (adicional).
    """
    if answer.field.form_default_field is True:
        raise ValidationError({'field': [
            'Campo selecionado não é adicional ao formulário.'
        ]})


def rule_3_resposta_com_tipo_correto(answer):
    """
    Resposta de campo com opções deve ser do tipo 'list'
    """
    value = answer.get_value()
    if not value:
        return

    field = answer.field
    if field.field_type in [
            field.FIELD_CHECKBOX_GROUP] and not isinstance(value, list):
        raise ValidationError({'value': [
            'Tipo de valor incorreto: O campo \'{}\' exige um registro de'
            ' valor do tipo \'list\''.format(field.label)
        ]})

    if field.field_type in [
        field.FIELD_INPUT_TEXT,
        field.FIELD_INPUT_PHONE,
        field.FIELD_INPUT_EMAIL,
        field.FIELD_INPUT_DATE,
        field.FIELD_INPUT_DATETIME,
        field.FIELD_RADIO_GROUP,
        field.FIELD_SELECT,
        field.FIELD_BOOLEAN,
        field.FIELD_TEXTAREA,
    ] and not isinstance(value, str):
        raise ValidationError({'value': [
            'Tipo de valor incorreto: O campo \'{}\' exige um registro de'
            ' valor do tipo \'string\''.format(field.label)
        ]})
