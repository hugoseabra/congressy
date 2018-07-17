import abc

from gatheros_subscription.models import Lot
from collections import OrderedDict


class DataError(object):
    """
        Define uma maneira de como os dados são verificados e validados,
        coletando os possiveis erross
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, data: OrderedDict) -> None:
        self.errors = {}
        self.valid = False
        self.data = data

    @abc.abstractmethod
    def is_valid(self):
        raise NotImplementedError('must define an is_valid to use this class')

    def get_errors(self):
        return self.errors

    def add_error(self, key, error):
        if key not in self.errors:
            self.errors[key] = []

        self.errors[key].append(error)


class DataValueIntegrityValidator(DataError):

    def __init__(self,
                 lot_pk: int,
                 extra_required_keys: dict = {},
                 *args, **kwargs) -> None:

        self.extra_keys = extra_required_keys
        self.lot = Lot.objects.get(pk=lot_pk)
        super().__init__(*args, **kwargs)

    def is_valid(self):
        # TODO implement clean logic here
        return self.valid


class LineKeyValidator(DataError):

    def __init__(self, valid_keys: list, *args, **kwargs) -> None:
        self.valid_keys = valid_keys
        super().__init__(*args, **kwargs)
        self.line = self.parse_line_keys()

    def parse_line_keys(self) -> dict:
        parsed_dict = {}

        for key, value in self.line.items():
            key = key.lower().strip()
            parsed_dict.update({key: value})

        return parsed_dict

    def is_valid(self):

        for key in self.valid_keys:
            found = self.line.get(key, False)

            if found is False:
                return False

        self.valid = True
        return self.valid


class DataErrorManager(object):
    """
        Gerencia a sequencia de validações de uma coleção de dados a serem
        processados
    """
    def __init__(self, valid_keys: list, data: OrderedDict) -> None:
        self.errors = {}
        self.valid = False
        self.data = data





