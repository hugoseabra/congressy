"""
    Testing the Partner model entity
"""

from django.test import TestCase

from partner.models import Partner
from partner.tests.mocks import MockFactory


class PartnerModelTest(TestCase):
    """ Main test implementation """

    def setUp(self):
        self.fake_factory = MockFactory()
        self.person = self.fake_factory._create_fake_person()

    def test_partner_creation(self):
        partner = Partner(person=self.person)
        self.assertIsNotNone(partner)
