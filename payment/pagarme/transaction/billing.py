class Billing:
    CORPORATION = 'corporation'
    INDIVIDUAL = 'individual'

    DOC_TYPES_BR_INDIVIDUAL = ['cpf']
    DOC_TYPES_BR_CORPORATION = ['cnpj']

    DOC_TYPES_INTERNATIONAL_INDIVIDUAL = ['id', 'passport']
    DOC_TYPES_INTERNATIONAL_CORPORATION = ['ein']

    BR_COUNTRY = 'br'

    def __init__(self,
                 name: str,
                 street: str,
                 zipcode: str,
                 city: str,
                 state: str,
                 street_number: str = None,
                 neighborhood: str = None,
                 complement: str = None,
                 country: str = None):

        self.name = name
        self.street = street
        self.street_number = street_number
        self.complement = complement
        self.neighborhood = neighborhood
        self.zipcode = zipcode
        self.city = city
        self.state = state
        self.country = country or self.BR_COUNTRY

        self.errors = dict()
        self._check_errors()

    def is_valid(self):
        self._check_errors()
        return len(self.errors) == 0

    def _check_errors(self):
        self.errors = dict()

        if self.country == self.BR_COUNTRY:
            if self.neighborhood is None:
                self.errors['neighborhood'] = 'Você deve informar o' \
                                              ' parâmetro "neighborhood",' \
                                              ' mesmo que seja uma string' \
                                              ' vazia.'

            if self.street_number is None:
                self.errors['street_number'] = 'Você deve informar o' \
                                               ' parâmetro "street_number",' \
                                               ' mesmo que seja uma string' \
                                               ' vazia.'

    def __iter__(self):

        if self.is_valid() is False:
            msg = 'Billing não está válido:'

            for k, v in self.errors.items():
                msg += ' {}: {}.'.format(k, v)

            raise Exception(msg)

        iters = {
            'name': self.name,
            'address': {
                'street': self.street,
                'zipcode': self.zipcode,
                'city': self.city,
                'state': self.state,
                'country': self.country,
            },
        }

        if self.complement:
            iters['address']['complement'] = self.complement

        if self.country == self.BR_COUNTRY:
            iters['address']['neighborhood'] = self.neighborhood or ''
            iters['address']['street_number'] = self.street_number or ''

        # now 'yield' through the items
        for x, y in iters.items():
            yield x, y
