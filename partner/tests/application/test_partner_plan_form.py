"""
     Partner Plan Form tests
"""
from django.test import TestCase

from partner.forms import PartnerPlanForm
from partner.tests.mocks import MockFactory


class PartnerPlanFormTest(TestCase):
    """ Partner Plan Form test implementation """

    def setUp(self):
        self.mock_factory = MockFactory()
        self.person = self.mock_factory._create_fake_person()

    def test_regular_form_validation(self):
        form = PartnerPlanForm(data={
            'percent': 5.5,
            'name': 'Fiver percent'
        })
        form.full_clean()
        self.assertTrue(form.is_valid())

