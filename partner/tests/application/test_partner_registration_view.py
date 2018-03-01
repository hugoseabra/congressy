"""
     Partner Registration View Tests
"""
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from faker import Faker
from random import randint

from gatheros_event.models import Person
from partner.models import Partner
from payment.models import BankAccount


class PartnerRegistrationViewTests(TestCase):
    """ Partner Registration View test implementation """

    def setUp(self):
        self.url = reverse('public:partner-registration')
        self.faker = Faker('pt_BR')
        self.name = self.faker.name()
        self.email = self.faker.free_email()
        self.phone = self.faker.phone_number()
        self.cpf = self.faker.cpf()

    def test_public_partner_registration_get_is_200_ok(self):
        """ Testa se está tudo ok com view com submissão GET. """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_public_partner_registration_post_200_ok(self):
        """ Testa se está tudo ok com view com submissão POST. """
        data = {
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'bank_code': BankAccount.CAIXA_ECONOMICA,
            'agency': str(randint(1000, 9999)),
            'agency_dv': '000',
            'account': str(randint(40000, 60000)),
            'account_dv': '001',
            'document_number': self.cpf,
            'legal_name': self.name,
            'type': BankAccount.CONTA_CORRENTE,
        }

        response = self.client.post(self.url, data, follow=True)
        self.assertContains(response, b'Cadastrado realizado com sucesso')
        self.assertEqual(response.status_code, 200)

        # Validating the persistence.
        person = Person.objects.get(name=self.name)

        self.assertIsNotNone(person)
        self.assertIsNotNone(Partner.objects.get(person=person))
        self.assertIsNotNone(User.objects.get(email=self.email))
