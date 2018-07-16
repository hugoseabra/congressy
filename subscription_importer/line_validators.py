import abc

from gatheros_subscription.models import Lot


class ValidatorMixin(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self,
                 line: dict,
                 lot_pk: int,
                 extra_required_keys: dict) -> None:
        self.errors = {}
        self.valid = False
        self.line = line
        self.extra_keys = extra_required_keys
        self.lot = Lot.objects.get(pk=lot_pk)
        super().__init__()

    @abc.abstractmethod
    def is_valid(self):
        raise NotImplementedError('must define an is_valid to use this class')

    def get_errors(self):
        return self.errors


class LineDataIntegrityValidator(ValidatorMixin):

    def is_valid(self):
        # TODO implement clean logic here
        return self.valid


class LineKeyValidator(ValidatorMixin):

    def is_valid(self):
        # TODO implement clean logic here
        return self.valid

