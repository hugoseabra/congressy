from datetime import datetime

from django.core.exceptions import ValidationError


def rule_1_data_inicial_antes_da_data_final(event):
    if event.date_end < event.date_start:
        raise ValidationError({'date_start': [
            'Data inicial deve anterior a data final'
        ]})


def rule_2_local_deve_ser_da_mesma_organizacao_do_evento(event):
    """
    Um evento não pode ter um local que seja de outra organização.
    """
    if event.place and event.place.organization != event.organization:
        raise ValidationError({'place': [
            'Evento e Local não são da mesma organização.'
        ]})


def rule_3_evento_data_final_posterior_atual(event, adding=True):
    if adding is True and event.date_end < datetime.now():
        raise ValidationError({'date_end': [
            'Não é possível cadastrar evento que já tenha se encerrado.'
        ]})


def rule_4_running_published_event_cannot_change_date_start(event):
    """
    Se evento está publicado e em andamento, não é possível mudar a
    data inicial.

    :param event: Event model
    :return: None
    """
    now = datetime.now()
    published = event.published
    running = event.date_start <= now <= event.date_end

    if published and running and event.has_changed('date_start'):
        raise ValidationError({'date_start': [
            'Não é possível alterar a data inicial de um evento em andamento.'
            ' Despublique o evento e altere a data inicial.'
        ]})
