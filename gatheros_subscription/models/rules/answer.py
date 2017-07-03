# pylint: disable=C0103
"""Regras de Negócios para Resposta de campo."""

from django.core.exceptions import ValidationError


def rule_1_mesma_organizacao(answer):
    """
    Resposta deve ser de um campo da mesma organização do evento da inscrição.
    """
    answer_org = answer.subscription.event.organization.pk
    field_org = answer.field.organization.pk
    if answer_org != field_org:
        raise ValidationError(
            {'field': ['Campo não pertence à organização da inscrição.']}
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
        field.FIELD_TEXTAREA,
    ] and not isinstance(value, str):
        raise ValidationError({'value': [
            'Tipo de valor incorreto: O campo \'{}\' exige um registro de'
            ' valor do tipo \'string\''.format(field.label)
        ]})

    if field.field_type in [
        field.FIELD_BOOLEAN,
    ] and not isinstance(value, bool):
        raise ValidationError({'value': [
            'Tipo de valor incorreto: O campo \'{}\' exige um registro de'
            ' valor do tipo \'boolean\''.format(field.label)
        ]})
