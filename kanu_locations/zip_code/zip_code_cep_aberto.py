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

        self.uri = 'cep?cep={}'.format(
            self.zip_code.replace('.', '').replace('-', '')
        )

        kwargs.update({
            'base_url': 'http://www.cepaberto.com/api/v3/',
            'api_key': '<cep-aberto-api-key>',
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

        if not result:
            raise CongressyException('CEP Inválido')

        if 'cidade' in result:
            city_data = result['cidade']
            if 'nome' in city_data:
                self.city_name = city_data['nome']
                self.city_name = str(self.city_name).upper()

        if 'estado' in result:
            state_data = result['estado']
            if 'sigla' in state_data:
                self.state_name = state_data['sigla']
                self.state_name = str(self.state_name).upper()

        if self.city_name and self.state_name:
            try:
                city_instance = City.objects.get(
                    Q(name__iexact=self.city_name) |
                    Q(name_ascii__iexact=self.city_name),
                    uf=self.state_name,
                )
                self.city_id = city_instance.pk

            except City.DoesNotExist:
                pass

        # {'cidade': {'ibge': '5208707', 'ddd': 62, 'nome': 'Goiânia'},
        #  'latitude': '-16.6733777', 'bairro': 'Jardim Novo Mundo',
        #  'logradouro': 'Avenida San Martin', 'cep': '74710040',
        #  'longitude': '-49.2137207', 'altitude': 762.8,
        #  'estado': {'sigla': 'GO'}}

        if 'logradouro' in result and result['logradouro']:
            self.street_name = str(result['logradouro']).upper()

        if 'bairro' in result and result['bairro']:
            self.neighborhood = str(result['bairro']).upper()

        self.zip_code_formatted = '{}{}-{}'.format(
            self.zip_code[:2],
            self.zip_code[2:5],
            self.zip_code[5:]
        )

    def get(self, endpoint):
        return self.request(method='GET', endpoint=endpoint)
