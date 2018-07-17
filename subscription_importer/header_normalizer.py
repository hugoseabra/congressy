from .constants import KEY_MAP


class HeaderNormalizer(object):
    """
        Essa classe tem a responsabilidade de normalizar os campos de um
        cabeçalho:
            - setar os nomes corretos das chaves do cabeçalho
            - fornecer informações de chaves invalidas
    """
    def __init__(self, header: list) -> None:
        self.header = header
        self.keys = []
        self.invalid_keys = []

    def has_valid(self):
        self._clean()
        return len(self.keys) > 0

    def _clean(self):

        for key in self.header:

            is_valid = False

            parsed_entry = key.lower().strip()

            for _, value in KEY_MAP.items():
                if parsed_entry in value['csv_keys']:
                    is_valid = True
                    break

            if is_valid:
                self.keys.append(parsed_entry)
            else:
                self.invalid_keys.append(key)
