"""
     Partner Registration Form tests
"""
from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from faker import Faker

from gatheros_event.models import Person
from partner.forms import PartnerRegistrationForm
from partner.models import Partner


class PartnerRegistrationFormTest(TestCase):
    """ Partner Registration Form test implementation """

    def setUp(self):
        self.faker = Faker()
        self.name = self.faker.name()
        self.email = self.faker.free_email()

    def test_regular_form_validation(self):

        form = PartnerRegistrationForm(data={
            'name': self.name,
            'email': self.email,
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
        })

        form.full_clean()
        self.assertTrue(form.is_valid())
        form.save()

        # Caixa de mensagens deve possuir dois emails, um enviado ao parceiro
        #  e um enviado ao time interno de vendas.
        self.assertEqual(len(mail.outbox), 2)

