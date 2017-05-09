from django.db import IntegrityError

from gatheros_event.models import Event
from .. import DefaultField


def rule_1_form_em_event_inscricao_desativada( form ):
    event = form.event
    if event.subscription_type == Event.SUBSCRIPTION_DISABLED:
        raise IntegrityError(
            'O evento {} está com as inscrições desativadas e não pode ter'
            ' formulários.'.format(event.name)
        )


def rule_2_form_possui_todos_campos_padrao( form ):
    """
    Garantia de que todas as inscrição terão as informações exigidas pelo
    sistema.
    """
    existing_fields = []
    for f in form.fields.all():
        existing_fields.append(f.name)

    for default_field in DefaultField.objects.all():
        if default_field.name not in existing_fields:
            raise IntegrityError(
                'O evento {} não possui os campos obrigatórios necessários.'
                    .format(form.event.name)
            )
