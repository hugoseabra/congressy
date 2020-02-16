from datetime import date


class Customer:
    CORPORATION = 'corporation'
    INDIVIDUAL = 'individual'

    DOC_TYPES_BR_INDIVIDUAL = ['cpf']
    DOC_TYPES_BR_CORPORATION = ['cnpj']

    DOC_TYPES_INTERNATIONAL_INDIVIDUAL = ['ID', 'Passport']
    DOC_TYPES_INTERNATIONAL_CORPORATION = ['ein']

    BR_COUNTRY = 'br'

    def __init__(self,
                 external_id: str,
                 name: str,
                 email: str,
                 doc_type: str,
                 doc_number: str,
                 phones: list = None,
                 country: str = None):

        self.external_id = external_id
        self.name = name
        self.email = email
        self.phones = phones
        self.doc_type = doc_type
        self.doc_number = doc_number

        self.country = country or self.BR_COUNTRY
        self.birthday = None

        self.customer_type = self.CORPORATION

        self.errors = dict()
        self._check_errors()

    def set_as_individual(self, birthday: date):
        self.customer_type = self.INDIVIDUAL
        self.birthday = birthday

        self._check_errors()

    def is_valid(self):
        self._check_errors()
        return len(self.errors) == 0

    def _check_errors(self):
        country = self.country.lower()
        dt = self.doc_type

        self.errors = dict()

        if self.customer_type == self.CORPORATION:

            if country == self.BR_COUNTRY:
                doc_types = self.DOC_TYPES_BR_CORPORATION
            else:
                doc_types = self.DOC_TYPES_INTERNATIONAL_CORPORATION

        else:
            if country == self.BR_COUNTRY:
                doc_types = self.DOC_TYPES_BR_INDIVIDUAL
            else:
                doc_types = self.DOC_TYPES_INTERNATIONAL_INDIVIDUAL

        if dt not in doc_types:
            self.errors['doc_type'] = \
                'Documento deve ser "{}". Tipo informado:' \
                ' {}.'.format(' ou '.join(doc_types), self.doc_type)

    def __iter__(self):
        if self.is_valid() is False:
            msg = 'Customer não está válido:'

            for k, v in self.errors.items():
                msg += ' {}: {}.'.format(k, v)

            raise Exception(msg)

        iters = {
            'external_id': self.external_id,
            'name': self.name,
            'email': self.email,
            'country': self.country.lower(),
            'documents': [
                {
                    'type': self.doc_type,
                    'number': self.doc_number,
                }
            ],
            'type': self.customer_type,
        }

        if self.phones:
            iters['phone_numbers'] = self.phones[0],

        if self.customer_type == self.INDIVIDUAL:
            assert isinstance(self.birthday, date), \
                '{} != date'.format(type(date))

            iters['birthday'] = self.birthday.strftime('%Y-%m-%d')

        # now 'yield' through the items
        for x, y in iters.items():
            yield x, y
