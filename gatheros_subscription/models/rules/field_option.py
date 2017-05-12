from django.core.exceptions import ValidationError


def rule_1_somente_campos_com_opcoes(option):
    if not option.field.with_options:
        raise ValidationError({'field': [
            'O campo {} não aceita opções.'.format(option.field.label)
        ]})
