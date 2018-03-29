""" Testes de serviços de aplicação do módulo de Afiliados. """

import random

from faker import Faker
from test_plus.test import TestCase
from payment.models import BankAccount
from affiliate import forms

faker = Faker('pt-BR')


class AffiliateFormTest(TestCase):
    """ Testa formulário de afiliado. """
    data = None

    def setUp(self):
        name = ' '.join(faker.words(nb=3))
        faker.cpf()

        self.data = {
            'name': name.title(),
            'gender': random.choice(('M', 'F')),
            'email': faker.safe_email(),
            'birth_date': faker.date('%d/%m/%Y'),
            'bank_code': BankAccount.BRADESCO,
            'agency': faker.ssn(),
            'agency_dv': random.randint(0, 9),
            'account': faker.ssn(),
            'account_dv': random.randint(0, 9),
            'legal_name': name.title(),
            'document_number': faker.cpf(),
            'account_type': BankAccount.CONTA_CORRENTE,
            'type_of_document': 'cpf',
        }

    def test_render(self):
        form = forms.AffiliateForm()

        for field in form:
            print(field.name)

        print(self.data)
