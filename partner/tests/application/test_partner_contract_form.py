"""
     Partner Contract Form tests
"""
from django.test import TestCase

from partner.forms import PartnerContractForm
from partner.tests.mocks import MockFactory


class PartnerContractFormTest(TestCase):
    """ Partner Contract Form test implementation """

    def setUp(self):
        self.mock_factory = MockFactory()
        self.person = self.mock_factory._create_fake_person()
        self.organization = self.mock_factory._create_fake_organization()
        self.partner = self.mock_factory._create_fake_partner(self.person)
        self.partner_plan = self.mock_factory._create_fake_partner_plan()
        self.event = self.mock_factory._create_fake_event(self.organization)

    def test_regular_form_validation(self):
        form = PartnerContractForm(data={
            'partner': self.partner.pk,
            'partner_plan': self.partner_plan.pk,
            'event': self.event.pk,
        })
        form.full_clean()
        self.assertTrue(form.is_valid())
