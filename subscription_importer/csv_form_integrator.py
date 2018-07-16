from gatheros_subscription.models import Lot
from .constants import REQUIRED_KEYS


class CSVFormIntegrator(object):

    def __init__(self, lot_pk: int) -> None:
        self.lot = Lot.objects.get(pk=lot_pk)
        self.event = self.lot.event
        self.form_config = self.event.formconfig
        super().__init__()

    def get_required_keys(self) -> list:
        keys = REQUIRED_KEYS
        
        config = self.form_config

        if config.phone:
            keys.append('phone')

        if config.city:
            keys.append('city')
            keys.append('uf')

        if config.cpf == config.CPF_REQUIRED:
            keys.append('cpf')

        if config.birth_date == config.BIRTH_DATE_REQUIRED:
            keys.append('birth_date')

        if config.address == config.ADDRESS_SHOW:
            keys.append('address')

        if config.institution == config.INSTITUTION_CNPJ_REQUIRED:
            keys.append('institution')

        if config.institution_cnpj == config.INSTITUTION_CNPJ_REQUIRED:
            keys.append('institution_cnpj')

        if config.function == config.FUNCTION_REQUIRED:
            keys.append('function')
        
        return keys
