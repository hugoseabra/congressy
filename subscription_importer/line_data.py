from collections import OrderedDict

from subscription_importer.constants import KEY_MAP


class LineData(object):
    """
        Essa classe é responsavel por preparar os dados em um iterável já
        mapeado os atributos já normalizados:
        
            - setar os nomes corretos das chaves do cabeçalho
            - fornecer informações de chaves invalidas
    """

    def __init__(self, raw_data: OrderedDict) -> None:

        self.__invalid_keys = []

        for raw_key, raw_value in raw_data.items():

            is_valid = False
            parsed_key = raw_key.lower().strip()

            for key, value in KEY_MAP.items():
                if parsed_key in value['csv_keys']:
                    is_valid = True
                    parsed_key = key
                    break

            if is_valid:
                setattr(self, parsed_key, raw_value)
            else:
                self.__invalid_keys.append(raw_key)

    def __iter__(self):
        for i in self.__dict__.items():
            yield i
