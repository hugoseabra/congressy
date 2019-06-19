import json
import os

from sync.entity_keys import (
    sync_file_keys,
    person_required_keys,
    subscription_required_keys,
    transaction_required_keys,
    attendance_service_required_keys, checkin_required_keys,
    checkout_required_keys, transaction_status_required_keys)


def check_file_sync_error(sync_file_path):
    """
    Verifica se arquivo de sincronização possui erros.

    1. Se arquivo existe
    2. Se arquivo é de extensão .json
    3. Se formatação do json está correta
    4. Se chaves do conteúdo json estão corretas
    5. Se existir chave, verificar se campos obrigatórios estão presentes.
    """
    if os.path.isfile(sync_file_path) is False:
        raise Exception('Arquivo não existe')

    file_split = sync_file_path.split('.')

    if len(file_split) < 1 or str(file_split[-1]).lower() != 'json':
        raise Exception('Arquivo não é uma extensão JSON')

    with open(sync_file_path) as json_file:
        try:
            all_data = json.loads(json_file.read())
        except ValueError as e:
            json_file.close()
            raise Exception('Arquivo inválido: {}'.format(e))

    error_keys = list()
    all_data_keys = list(all_data.keys())

    for key in sync_file_keys:
        if key not in all_data_keys:
            error_keys.append(key)
            continue

        data_keys = list(sync_file_keys[key].keys())

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
            if key2 not in data_keys:
                error_keys.append(
                    '{} possui campos faltando: {}'.format(key.upper(), key2)
                )

    if error_keys:
        raise Exception('Arquivo inválido. Chaves desconhecidas: {}'.format(
            ", ".join(error_keys),
        ))


def get_sync_warning(sync_file_path):
    """
    Recupera mensagem de alerta relevantes do conteúdo de um arquivo de
    sincronização.

    Este helper
    """

    error_keys = list()
    all_data_keys = list(all_data.keys())

    for key in sync_file_keys:
        if key not in all_data_keys:
            error_keys.append(key)
            continue

        data_keys = list(sync_file_keys[key].keys())

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
            if key2 not in data_keys:
                error_keys.append(
                    '{} possui campos faltando: {}'.format(key.upper(), key2)
                )

    if error_keys:
        return 'Arquivo inválido. Chaves desconhecidas: {}'.format(
            ", ".join(error_keys),
        )

    return None
