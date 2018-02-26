"""
    Testing the Partner model entity
"""

from partner.models import Partner
from django.test import TestCase
from gatheros_event.models import Person
from partner import constants


class PartnerModelTest(TestCase):
    """ Main test implementation """

    # Fixtures from gatheros_event
    fixtures = [
        '005_user',
        '006_person',
    ]

    def setUp(self):
        self.person = Person.objects.first()
        self.assertIsNotNone(self.person)

    def test_partner_creation(self):
        partner = Partner(person=self.person)
        self.assertIsNotNone(partner)
        self.assertEqual(partner.status, constants.NON_ACTIVE)
        self.assertFalse(partner.approved)
