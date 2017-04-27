from django.core.exceptions import ValidationError


def rule_1_data_inicial_antes_da_data_final(entity):
    if entity.date_end < entity.date_start:
        raise ValidationError({'date_start': ['Data inicial deve anterior a data final']})


def rule_2_local_deve_ser_da_mesma_organizacao_do_evento(entity):
    """
    Um evento não pode ter um local que seja de outra organização.
    """
    if entity.place and entity.place.organization != entity.organization:
        raise ValidationError({'place': ['Local do evento não pertence a sua organização']})
