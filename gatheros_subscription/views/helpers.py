import csv

ALLOWED_KEYS = [
    'nome',
    'email',
    'data nasc',
    'cpf',
    'doc internacional',
    'cep',
    'bairro',
    'número',
    'rua/logradouro',
    'complemento',
    'cidade'
    'uf',
    'celular',
    'função/cargo',
    'cnpj',
    'instituição/empresa',
    'status',
    'credenciado',
]


def validate_table_keys(line: list) -> dict:
    main_dict = {}

    for key in line:

        lower_key = key.lower().strip()
        is_valid = False
        index = line.index(key)

        if lower_key in ALLOWED_KEYS:
            is_valid = True
            key = lower_key

        current_dict = {
            'valid': is_valid,
            'name': key,
        }

        main_dict.update({index: current_dict})

    return main_dict


def parse_file(encoded_content: str, delimiter: str, quotechar: str):

        content = encoded_content.splitlines()

        first_line = content[0].split(delimiter)

        table_keys = validate_table_keys(first_line)

        valid_keys = []

        for entry in table_keys.items():
            if entry[1]['valid']:
                valid_keys.append(entry[1]['name'])

        main_dict = {}
        for key in valid_keys:
            main_dict[key] = []

        reader = csv.DictReader(
            content,
            delimiter=delimiter,
            quotechar=quotechar,
        )

        for row in reader:
            for item in row.items():

                possible_key = item[0]
                if possible_key:
                    possible_key = possible_key.lower().strip()

                possible_value = item[1]
                if possible_value:
                    possible_value.strip()

                if possible_value and possible_key in valid_keys:
                    main_dict[possible_key].append(possible_value)

        return main_dict
