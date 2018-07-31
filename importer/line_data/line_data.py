from collections import OrderedDict

from django.contrib.auth.models import User

from gatheros_subscription.models import FormConfig, Lot
from importer.constants import KEY_MAP
from importer.forms import CSVSubscriptionForm
from importer.helpers import get_required_keys


class LineData(object):
    """
        Essa classe é responsavel por preparar os dados em um iterável já
        mapeado os atributos já normalizados:
        
            - setar os nomes corretos das chaves do cabeçalho
            - fornecer informações de chaves invalidas

        Além de também realizar a persistencia através do método save.
    """

    def __init__(self, raw_data: OrderedDict) -> None:

        self.__invalid_keys = []
        self.__errors = None

        for raw_key, raw_value in raw_data.items():

            parsed_key = raw_key.lower().strip()
            is_valid = False

            for key, value in KEY_MAP.items():
                if parsed_key in value['csv_keys']:
                    is_valid = True
                    parsed_key = key
                    break

            if is_valid:
                setattr(self, parsed_key, raw_value)
            else:
                self.__invalid_keys.append(raw_key)

    def get_errors(self):
        return self.__errors

    def save(self,
             form_config: FormConfig,
             lot: Lot,
             user: User,
             commit: bool = False):
        """

        Esse método faz a delegação da persistencia para um Form, passando pra
        ele os campos obrigatorios através de um objeto FormConfig.

        :param form_config: Object FormConfig
        :param lot: Object Lot
        :param user: Object User
        :param commit: Boolean
        :return: None
        """

        required_keys = get_required_keys(form_config=form_config)

        data = {'lot_id': lot.pk}

        for key, value in self:
            data.update({key: value})

        form = CSVSubscriptionForm(
            event=lot.event,
            user=user,
            required_keys=required_keys,
            data=data,
        )

        if form.is_valid():
            if commit:
                form.save()
        else:
            self.__errors = form.errors

    def __iter__(self):
        for i in self.__dict__.items():
            # Ignore mangled invalid keys
            if not i[0].startswith('_'):
                yield i

    def get_invalid_keys(self):
        return self.__invalid_keys
