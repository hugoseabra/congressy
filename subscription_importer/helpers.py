from .constants import KEY_MAP
from .exceptions import MappingNotFoundError


def get_mapping_key_from_csv_key(key):
    for map_key, mapping in KEY_MAP.items():
        if key in mapping['csv_keys']:
            return map_key, KEY_MAP[map_key]

    raise MappingNotFoundError(key)


def get_required_keys_mappings(form_config) -> list:
    required_keys_mapping = []
    required_keys = form_config.get_required_keys()

    for key in required_keys:
        mapping = KEY_MAP.get(key, None)
        if mapping is None:
            raise MappingNotFoundError(key)
        required_keys_mapping.append(mapping)

    return required_keys_mapping
