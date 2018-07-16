from .constants import KEY_MAP
from .exceptions import MappingNotFoundError


def get_mapping_key_from_csv_key(key):
    for map_key, mapping in KEY_MAP.items():
        if key in mapping['csv_keys']:
            return map_key, KEY_MAP[map_key]

    raise MappingNotFoundError(key)



