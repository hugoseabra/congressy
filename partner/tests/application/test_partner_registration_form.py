"""
     Partner Registration Forms tests
"""
from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from faker import Faker
from random import randint

from gatheros_event.models import Person
from partner.forms import PartnerRegistrationForm, FullPartnerRegistrationForm
from partner.models import Partner
from payment.models import BankAccount


class PartnerRegistrationFormTest(TestCase):
    """ Partner Registration Form test implementation """

    def setUp(self):
        self.faker = Faker('pt_BR')
        self.name = self.faker.name()
        self.email = self.faker.free_email()
        self.phone = self.faker.phone_number()

    def test_regular_form_validation(self):

        form = PartnerRegistrationForm(data={
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
        })

        form.full_clean()
        self.assertTrue(form.is_valid())
        form.save()

        self.assertIsNotNone(User.objects.get(email=self.email))

        person = Person.objects.get(email=self.email)
        self.assertIsNotNone(Partner.objects.get(person=person))

    def test_public_partner_registration_sending_partner_email(self):
        """ Testa se está tudo ok emails após o registro feito pelo parceiro """

        form = PartnerRegistrationForm(data={
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
        })

        form.full_clean()
        self.assertTrue(form.is_valid())
        form.save()

        # Caixa de mensagens deve possuir dois emails, um enviado ao parceiro
        #  e um enviado ao time interno de vendas.
        self.assertEqual(len(mail.outbox), 2)


class PartnerFullRegistrationFormTest(TestCase):
    """ Partner Registration Form test implementation """

    def setUp(self):
        self.faker = Faker('pt_BR')
        self.name = self.faker.name()
        self.email = self.faker.free_email()
        self.phone = self.faker.phone_number()
        self.cpf = '21375415301'
        self.bank_code = BankAccount.CAIXA_ECONOMICA
        self.agency = str(randint(1000, 9999))
        self.agency_dv = '000'
        self.account = str(randint(40000, 60000))
        self.account_dv = '01'
        self.account_type = BankAccount.CONTA_CORRENTE

    def test_regular_form_validation(self):

        form = FullPartnerRegistrationForm(data={
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
            'type': self.account_type,
        })

        self.assertTrue(form.is_valid())
        form.save()

        self.assertIsNotNone(User.objects.get(email=self.email))

        person = Person.objects.get(email=self.email)
        self.assertIsNotNone(Partner.objects.get(person=person))

    def test_public_partner_registration_sending_partner_email(self):
        """ Testa se está tudo ok emails após o registro feito pelo parceiro """

        form = PartnerRegistrationForm(data={
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
        })

        form.full_clean()
        self.assertTrue(form.is_valid())
        form.save()

        # Caixa de mensagens deve possuir dois emails, um enviado ao parceiro
        #  e um enviado ao time interno de vendas.
        self.assertEqual(len(mail.outbox), 2)

