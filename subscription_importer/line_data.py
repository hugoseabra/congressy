from collections import OrderedDict

from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from csv_importer.forms import CSVSubscriptionForm
from gatheros_subscription.models import FormConfig, Lot
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
        self.__errors = []
        self.__valid = False

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

    def __iter__(self):
        for i in self.__dict__.items():
            # Ignore mangled invalid keys
            if not i[0].startswith('_'):
                yield i

    def get_invalid_keys(self):
        return self.__invalid_keys

    def save(self,
             form_config: FormConfig,
             lot: Lot,
             user: User,
             commit: bool = False):

        required_keys = form_config.get_required_keys()

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
            self.__valid = True
            if commit:
                form.save()
        else:
            for key, error in form.errors.items():
                error_string = _(error[0])
                self.__errors.append({key: error_string})

    def is_valid(self):
        return self.__valid

    def get_errors(self):
        return self.__errors
