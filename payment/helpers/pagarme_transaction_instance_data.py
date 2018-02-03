import uuid

import absoluteuri
from django.conf import settings

from gatheros_event.models import Organization
from payment.exception import TransactionError

congressy_id = settings.PAGARME_RECIPIENT_ID


class PagarmeTransactionInstanceData:

    # @TODO add international phone number capability

    def __init__(self, person, extra_data):

        self.person = person
        self.extra_data = extra_data

        self._get_organization()
        self._get_transaction_type()
        self._parametrize_instance_data()

    def _get_organization(self):

        if 'organization' not in self.extra_data:
            raise TransactionError(message="No organization")
        self.organization = Organization.objects.get(pk=self.extra_data['organization'])

        if not self.organization.bank_account_id:
            raise TransactionError(message="Organization has no bank account")

    def _get_transaction_type(self):

        allowed_payment_methods = ['boleto', 'credit_card']

        if 'transaction_type' not in self.extra_data:
            raise TransactionError(message='No transaction type')

        if self.extra_data['transaction_type'] not in allowed_payment_methods:
            raise TransactionError(message='Transaction type not allowed')

        self.transaction_type = self.extra_data['transaction_type']

    def _parametrize_instance_data(self):

        transaction_id = uuid.uuid4()

        postback_url = absoluteuri.reverse('public:payment_postback_url', kwargs={
            'uidb64': transaction_id
        })

        self.transaction_instance_data = {

            "customer": {
                "name": self.person.name,
                "type": "individual",
                "country": "br",
                "email": self.person.email,
                "documents": [
                    {
                        "type": "cpf",
                        "number": self.person.cpf,
                    }
                ],
                "phone_numbers": [
                    "+55" + self.person.phone.replace(" ", "").replace('(', '').replace(')',
                                                                                        '').replace(
                        '-', '')],
                "birthday": self.person.birth_date.strftime('%Y-%m-%d'),
            },

            "postback_url": postback_url,

            "billing": {
                "name": self.person.name,
                "address": {
                    "country": "br",
                    "state": self.person.city.uf.lower(),
                    "city": self.person.city.name.lower().capitalize(),
                    "neighborhood": self.person.village,
                    "street": self.person.street,
                    "street_number": str(self.person.number),
                    "zipcode": self.person.zip_code
                }
            },

            "items": [
                {
                    "id": str(transaction_id),
                    "title": "Inscrição do Evento: " + self.organization.name,
                    "unit_price": self.extra_data['amount'],
                    "quantity": 1,
                    "tangible": False
                }
            ],

            "split_rules": [
                {
                    "recipient_id": congressy_id,
                    "percentage": 10,
                    "liable": True,
                    "charge_processing_fee": True
                },
                {
                    "recipient_id": self.organization.recipient_id,
                    "percentage": 90,
                    "liable": True,
                    "charge_processing_fee": False
                }
            ]

        }

        if self.transaction_type == 'credit_card':

            self.transaction_instance_data['payment_method'] = 'credit_card'
            self.transaction_instance_data['price'] = self.extra_data['amount']
            self.transaction_instance_data['card_hash'] = self.extra_data['card_hash']

        if self.transaction_type == 'boleto':
            self.transaction_instance_data['payment_method'] = 'boleto'
            self.transaction_instance_data['amount'] = self.extra_data['amount']
