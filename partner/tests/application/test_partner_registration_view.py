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
        self.cpf = '21375415301'
        self.bank_code = BankAccount.CAIXA_ECONOMICA
        self.agency = str(randint(1000, 9999))
        self.agency_dv = str(randint(0, 9))
        self.account = str(randint(40000, 60000))
        self.account_dv = str(randint(0, 9))
        self.account_type = BankAccount.CONTA_CORRENTE

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
            'bank_code': self.bank_code,
            'agency': self.agency,
            'agency_dv': self.agency_dv,
            'account': self.account,
            'account_dv': self.account_dv,
            'document_number': self.cpf,
            'legal_name': self.name,
            'account_type': self.account_type,
        }

        response = self.client.post(self.url, data, follow=True)
        self.assertContains(response, b'Cadastrado realizado com sucesso')
        self.assertEqual(response.status_code, 200)

        # Validating the persistence.
        person = Person.objects.get(name=self.name)

        self.assertIsNotNone(person)
        self.assertIsNotNone(Partner.objects.get(person=person))
        self.assertIsNotNone(User.objects.get(email=self.email))
