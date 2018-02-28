"""
     Partner Registration Form tests
"""
from django.test import TestCase

from partner.forms import PartnerRegistrationForm
from django.contrib.auth.models import User
from gatheros_event.models import Person
from partner.models import Partner
from partner.tests.mocks import MockFactory
from faker import Faker


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

