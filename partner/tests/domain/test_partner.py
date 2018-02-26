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

    def test_person_is_partner_only_once(self):

        partner = Partner(person=self.person)
        partner2 = Partner(person=self.person)

        partner.save()
        partner2.save()

        self.assertEqual(partner.pk, partner2.pk)

    def test_partner_activation_and_deactivation(self):
        partner = Partner(person=self.person)
        partner.active = True
        partner.save()
        self.assertTrue(partner.active)
        partner.active = False
        partner.save()
        self.assertFalse(partner.active)

    def test_partner_change_status(self):
        partner = Partner(person=self.person)
        partner.save()
        self.assertEqual(partner.status, constants.NON_ACTIVE)

        partner.status = constants.ACTIVE
        partner.save()
        self.assertEqual(partner.status, constants.ACTIVE)

        partner.status = constants.SUSPENDED
        partner.save()
        self.assertEqual(partner.status, constants.SUSPENDED)
