from gatheros_subscription.models import Lot
from .constants import REQUIRED_KEYS, KEY_MAP
from .exceptions import MappingNotFoundError


class CSVFormIntegrator(object):

    def __init__(self, lot_pk: int) -> None:
        self.lot = Lot.objects.get(pk=lot_pk)
        self.event = self.lot.event
        self.form_config = self.event.formconfig
        super().__init__()

    def get_required_keys(self) -> list:
        required_keys = REQUIRED_KEYS
        required_keys_mapping = []

        config = self.form_config

        if config.phone:
            required_keys.append('phone')

        if config.city:
            required_keys.append('city')
            required_keys.append('uf')

        if config.cpf == config.CPF_REQUIRED:
            required_keys.append('cpf')

        if config.birth_date == config.BIRTH_DATE_REQUIRED:
            required_keys.append('birth_date')

        if config.address == config.ADDRESS_SHOW:
            required_keys.append('address')

        if config.institution == config.INSTITUTION_CNPJ_REQUIRED:
            required_keys.append('institution')

        if config.institution_cnpj == config.INSTITUTION_CNPJ_REQUIRED:
            required_keys.append('institution_cnpj')

        if config.function == config.FUNCTION_REQUIRED:
            required_keys.append('function')

        for key in required_keys:
            mapping = KEY_MAP.get(key, None)
            if mapping is None:
                raise MappingNotFoundError(key)
            required_keys_mapping.append(mapping)

        return required_keys_mapping
