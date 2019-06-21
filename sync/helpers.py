import json

from django.core.files import File

from sync.entity_keys import (
    sync_file_keys,
    person_required_keys,
    subscription_required_keys,
    transaction_required_keys,
    attendance_service_required_keys, checkin_required_keys,
    checkout_required_keys, transaction_status_required_keys,
    person_other_keys, subscription_other_keys, transaction_other_keys)


def check_file_sync_error(sync_file: File):
    """
    Verifica se arquivo de sincronização possui erros.

    1. Se arquivo existe
    2. Se arquivo é de extensão .json
    3. Se formatação do json está correta
    4. Se chaves do conteúdo json estão corretas
    5. Se existir chave, verificar se campos obrigatórios estão presentes.
    """
    try:
        all_data = json.loads(sync_file.read().decode('utf-8'))
    except ValueError as e:
        raise Exception('Arquivo inválido: {}'.format(e))

    error_keys = dict()
    all_data_keys = list(all_data.keys())

    for key in sync_file_keys:
        if key not in error_keys:
            error_keys[key] = list()

        if key not in all_data_keys:
            error_keys[key].append('{} não encontrado.'.format(key))
            continue

        data_keys = list(all_data[key].keys())

        if not data_keys:
            continue

        if key == 'persons':
            checkable_keys = person_required_keys
        elif key == 'subscriptions':
            checkable_keys = subscription_required_keys
        elif key == 'transactions':
            checkable_keys = transaction_required_keys
        elif key == 'transaction_statuses':
            checkable_keys = transaction_status_required_keys
        elif key == 'attendance_services':
            checkable_keys = attendance_service_required_keys
        elif key == 'checkins':
            checkable_keys = checkin_required_keys
        elif key == 'checkouts':
            checkable_keys = checkout_required_keys
        else:
            checkable_keys = list()

        for key2 in checkable_keys:
            if key2 in data_keys:
                continue

            error_keys[key].append('"{}"'.format(key2))

    if error_keys:
        error_keys_list = list()

        for key, error_list in error_keys.items():
            if not error_list:
                continue

            error_keys_list.append(
                'Errors em {}: {} não encontrados.'.format(
                    key, ", ".join(error_list)
                )
            )

        if error_keys_list:
            raise Exception(", ".join(error_keys_list))


def get_sync_warning(sync_file: File):
    """
    Recupera mensagem de alerta relevantes do conteúdo de um arquivo de
    sincronização.

    Este helper parte do suposto de que o arquivo de sincronização já é válido.
    """

    try:
        all_data = json.loads(sync_file.read().decode('utf-8'))
    except ValueError as e:
        raise Exception('Arquivo inválido: {}'.format(e))

    warning_keys = list()

    for key in sync_file_keys:
        data_keys = list(all_data[key].keys())

        if not data_keys:
            continue

        if key == 'persons':
            checkable_keys = person_other_keys
        elif key == 'subscriptions':
            checkable_keys = subscription_other_keys
        elif key == 'transactions':
            checkable_keys = transaction_other_keys
        else:
            checkable_keys = list()

        for key2 in checkable_keys:
            if key2 not in data_keys:
                warning_keys.append(
                    '{} possui campos ignorados: {}'.format(key.upper(), key2)
                )

    if warning_keys:
        return 'Atenção: {}'.format(", ".join(warning_keys), )

    return None
