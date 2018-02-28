"""
     Partner Contract Form tests
"""
from django.test import TestCase

from partner.forms import PartnerContractForm
from partner.tests.mocks import MockFactory


class PartnerContractFormTest(TestCase):
    """
        Partner Contract Form test implementation
        Business rule #1:  The sum of all partners of the event must not exceed
                            the Congressy defined percentage  of the amount of
                            the total amount
    """

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

    # Business Rule #1
    def test_percent_plan_exceeds_defined_percentage(self):
        bad_plan = self.mock_factory._create_fake_partner_plan(percentage=30.5)
        form = PartnerContractForm(data={
            'partner': self.partner.pk,
            'partner_plan': bad_plan.pk,
            'event': self.event.pk,
        })
        form.full_clean()
        self.assertFalse(form.is_valid())

    # Business Rule #1
    def test_does_exceed_defined_percentage(self):
        staging_plan = self.mock_factory._create_fake_partner_plan(
            percentage=15)
        bad_plan = self.mock_factory._create_fake_partner_plan(percentage=5.1)
        good_plan = self.mock_factory._create_fake_partner_plan(percentage=5)

        # Staging plan
        form = PartnerContractForm(data={
            'partner': self.partner.pk,
            'partner_plan': staging_plan.pk,
            'event': self.event.pk,
        })
        form.full_clean()
        self.assertTrue(form.is_valid())
        form.save()

        # Bad Plan
        form = PartnerContractForm(data={
            'partner': self.partner.pk,
            'partner_plan': bad_plan.pk,
            'event': self.event.pk,
        })
        form.full_clean()
        self.assertFalse(form.is_valid())

        # Good Plan
        form = PartnerContractForm(data={
            'partner': self.partner.pk,
            'partner_plan': good_plan.pk,
            'event': self.event.pk,
        })
        form.full_clean()
        self.assertTrue(form.is_valid())
        form.save()





