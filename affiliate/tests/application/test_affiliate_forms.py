""" Testes de serviços de aplicação do módulo de Afiliados. """

import random

from faker import Faker
from test_plus.test import TestCase
from payment.models import BankAccount
from affiliate import forms
from affiliate.models import Affiliate

faker = Faker('pt-BR')


class AffiliateFormTest(TestCase):
    """ Testa formulário de afiliado. """
    data = None

    def setUp(self):
        name = ' '.join(faker.words(nb=3))
        faker.cpf()

        self.data = {
            'type_of_document': False, # sabe-se lá pq isso é CPF
            'name': name.title(),
            'gender': random.choice(('M', 'F')),
            'email': faker.safe_email(),
            'birth_date': faker.date('%d/%m/%Y'),
            'bank_code': BankAccount.BRADESCO,
            'agency': faker.ssn()[0:5],
            'agency_dv': random.randint(0, 9),
            'account': '38829',
            'account_dv': random.randint(0, 9),
            'legal_name': name.title(),
            'document_number': '118.433.900-78',
            'account_type': BankAccount.CONTA_CORRENTE,
        }

    def test_save(self):

        form = forms.AffiliateForm(data=self.data)

        if not form.is_valid():
            self.fail(form.errors)

        self.assertIsInstance(form.save(), Affiliate)
