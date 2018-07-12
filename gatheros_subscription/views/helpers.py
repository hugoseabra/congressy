
class MappingNotFoundError(Exception):
    pass


KEY_MAP = {
    'name': {
        'verbose_name': 'Nome',
        'description': 'Nome do participante',
        'csv_keys': ['nome'],
        'possible_values': [],
    },

    'email': {
        'verbose_name': 'Email',
        'description': 'Email do participante',
        'csv_keys': ['email', 'e-mail'],
        'possible_values': [],
    },
}

REQUIRED_KEYS = [
    'name',
    'email',
]


def get_mapping_key_from_csv_key(key):

    for map_key, mapping in KEY_MAP.items():
        if key in mapping['csv_keys']:
            return map_key, KEY_MAP[map_key]

    raise MappingNotFoundError


