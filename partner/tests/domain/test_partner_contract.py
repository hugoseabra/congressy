"""
    Testing the Partner Contract model entity
"""

from django.test import TestCase

from partner.models import PartnerContract
from partner.tests.mocks import MockFactory


class PartnerContractModelTest(TestCase):
    """ Main test implementation """

    def setUp(self):
        self.fake_factory = MockFactory()
        self.person = self.fake_factory._create_fake_person()
        self.assertIsNotNone(self.person)
        self.organization = self.fake_factory._create_fake_organization()
        self.assertIsNotNone(self.organization)
        self.partner = self.fake_factory._create_fake_partner(
            person=self.person)
        self.assertIsNotNone(self.partner)
        self.partner_plan = self.fake_factory._create_fake_partner_plan()
        self.assertIsNotNone(self.partner_plan)
        self.event = self.fake_factory._create_fake_event(
            organization=self.organization)
        self.assertIsNotNone(self.event)

    def test_partner_contract_creation(self):
        partner_contract = PartnerContract(
            partner=self.partner,
            partner_plan=self.partner_plan,
            event=self.event
        )

        partner_contract.save()
        self.assertIsNotNone(partner_contract)
