from django.db.models import Q

from kanu_locations.models import City
from .exceptions import CongressyException
from .http import Resource


class ZipCode(Resource):
    """
    Valor de objeto resgatado a partir da integração de busca com massagem.
    """

    def __init__(self, zip_code: str, *args, **kwargs):
        self.zip_code = ''.join(*[filter(str.isalnum, zip_code)])
        self.zip_code_formatted = None
        self.street_name = None
        self.complement = None
        self.neighborhood = None
        self.city_name = None
        self.state_name = None
        self.city_id = None

        self.uri = '{}/json/unicode/'.format(self.zip_code)

        kwargs.update({
            'base_url': 'https://viacep.com.br/ws/'
        })
        super().__init__(*args, **kwargs)

    @property
    def data(self):
        return {
            'street_name': self.street_name,
            'complement': self.complement,
            'neighborhood': self.neighborhood,
            'city_id': self.city_id,
            'city_name': self.city_name,
            'state_name': self.state_name,
            'zip_code': self.zip_code,
            'zip_code_formatted': self.zip_code_formatted,
        }

    def process(self):
        result = self.get(self.uri)

        if 'erro' in result and result['erro'] is True:
            raise CongressyException('CEP Inválido')

        map_keys = {
            'logradouro': 'street_name',
            'complemento': 'complement',
            'bairro': 'neighborhood',
            'localidade': 'city_name',
            'uf': 'state_name',
            'cep': 'zip_code_formatted',
        }

        city_name = None
        city_uf = None

        for key, local_key in map_keys.items():
            if key in result and hasattr(self, local_key):
                value = str(result[key]).upper()
                if key == 'localidade':
                    city_name = value

                if key == 'uf':
                    city_uf = value

                setattr(self, local_key, value)

        if city_name and city_uf:
            try:
                city_instance = City.objects.get(
                    Q(name__icontains=city_name) |
                    Q(name_ascii__icontains=city_name),
                    uf=city_uf,
                )
                self.city_id = city_instance.pk

            except City.DoesNotExist:
                pass

    def get(self, endpoint):
        return self.request(method='GET', endpoint=endpoint)
