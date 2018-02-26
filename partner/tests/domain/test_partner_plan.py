"""
    Testing the Partner Plan model entity
"""

from django.test import TestCase
from faker import Faker

from gatheros_event.models import Person
from partner.models import PartnerPlan, Partner


class PartnerPlanModelTest(TestCase):
    """ Main test implementation """

    def _create_fake_person(self):
        person = Person(name=self.fake_factory.name())
        person.save()
        return person

    def setUp(self):
        self.fake_factory = Faker()
        self.person = self._create_fake_person()
        self.partner = Partner(person=self.person).save()

    def test_partner_plan_creation(self):
        partner_plan = PartnerPlan(name='Plano #1', percent=5.2)
        partner_plan.save()
        self.assertIsNotNone(partner_plan)
