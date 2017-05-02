from django.core.exceptions import ValidationError
from django.db import IntegrityError


def rule_1_campo_inscricao_formulario_mesmo_evento( answer ):
    answer_event = answer.subscription.event
    field_event = answer.field.form.event
    if answer_event != field_event:
        raise ValidationError(
            {'field': ['Campo não pertence ao evento \'{}\'.'.format(field_event.name)]}
        )


def rule_2_resposta_apenas_se_campo_adicional( answer ):
    if answer.field.form_default_field is True:
        raise ValidationError({'field': ['Campo selecionado não é adicional ao formulário.']})


def rule_3_resposta_com_tipo_correto( answer ):
    value = answer.get_value()
    if not value:
        return

    field = answer.field
    if field.type in [field.FIELD_CHECKBOX_GROUP] and type(value) is not list:
        raise ValidationError({'value': [
            'Tipo de valor incorreto: O campo \'{}\' exige um registro de valor do tipo \'list\''.format(field.label)
        ]})

    if field.type in [
        field.FIELD_INPUT_TEXT,
        field.FIELD_INPUT_PHONE,
        field.FIELD_INPUT_EMAIL,
        field.FIELD_INPUT_DATE,
        field.FIELD_INPUT_DATETIME,
        field.FIELD_RADIO_GROUP,
        field.FIELD_SELECT,
        field.FIELD_BOOLEAN,
        field.FIELD_TEXTAREA,
    ] and type(value) is not str:
        raise ValidationError({'value': [
            'Tipo de valor incorreto: O campo \'{}\' exige um registro de valor do tipo \'string\''.format(field.label)
        ]})
