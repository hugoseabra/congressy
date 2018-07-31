from .constants import KEY_MAP, REQUIRED_KEYS


class MappingNotFoundError(Exception):
    def __init__(self, key, *args: object, **kwargs: object) -> None:
        self.message = '{} not found'.format(key)
        self.key = key
        super().__init__(*args, **kwargs)


def get_mapping_from_csv_key(key):
    for map_key, mapping in KEY_MAP.items():
        if key in mapping['csv_keys']:
            return map_key, KEY_MAP[map_key]

    raise MappingNotFoundError(key)


def get_required_keys(form_config) -> list:
    found_keys = []
    required_keys = REQUIRED_KEYS
    form_config_keys = form_config.get_required_keys()
    required_keys.extend(
        x for x in form_config_keys if x not in required_keys)

    for key in required_keys:
        mapping = KEY_MAP.get(key, None)
        if mapping is None:
            raise MappingNotFoundError(key)
        found_keys.append(key)

    return found_keys


def get_required_keys_mappings(form_config) -> list:
    required_keys_mapping = []

    required_keys = get_required_keys(form_config)

    for key in required_keys:
        mapping = KEY_MAP.get(key, None)
        if mapping is None:
            raise MappingNotFoundError(key)
        required_keys_mapping.append(mapping)

    return required_keys_mapping
