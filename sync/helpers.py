import json

from django.core.files import File

from sync.entity_keys import (
    sync_file_keys,
    sync_schema_keys,
)


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

        for data_item in all_data[key]:
            data_keys = list(data_item.keys())

            if not data_keys:
                continue

            for sync_schema_key in sync_schema_keys:
                if sync_schema_key in data_keys:
                    continue

                error_keys[key].append('"{}"'.format(sync_schema_key))

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
