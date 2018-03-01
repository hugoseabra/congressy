"""
    Testing the Partner Plan model entity
"""

from django.test import TestCase

from partner.models import PartnerPlan
from partner.tests.mocks import MockFactory


class PartnerPlanModelTest(TestCase):
    """ Main test implementation """

    def setUp(self):
        self.fake_factory = MockFactory()
        self.person = self.fake_factory._create_fake_person()
        self.partner = self.fake_factory._create_fake_partner(
            person=self.person)

    def test_partner_plan_creation(self):
        name = 'Plano #1'
        partner_plan = PartnerPlan(name=name, percent=5.2)
        partner_plan.save()
        self.assertEqual(partner_plan.__str__(), name)
        self.assertIsNotNone(partner_plan)
