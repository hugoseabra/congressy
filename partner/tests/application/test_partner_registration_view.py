"""
     Partner Registration View Tests
"""
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from faker import Faker

from gatheros_event.models import Person
from partner.models import Partner


class PartnerRegistrationViewTests(TestCase):
    """ Partner Registration View test implementation """

    def setUp(self):
        self.url = reverse('public:partner-registration')
        self.faker = Faker()
        self.name = self.faker.name()
        self.email = self.faker.free_email()

    def test_public_partner_registration_get_is_200_ok(self):
        """ Testa se está tudo ok com view com submissão GET. """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_public_partner_registration_post_200_ok(self):
        """ Testa se está tudo ok com view com submissão POST. """
        data = {
            'name': self.name,
            'email': self.email
        }

        response = self.client.post(self.url, data, follow=True)
        self.assertContains(response, b'Cadastrado realizado com sucesso')
        self.assertEqual(response.status_code, 200)

        # Validating the persistence.
        person = Person.objects.get(name=self.name)

        self.assertIsNotNone(person)
        self.assertIsNotNone(Partner.objects.get(person=person))
        self.assertIsNotNone(User.objects.get(email=self.email))
