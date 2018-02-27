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


    def test_regular_form_validation(self):
        form = PartnerContractForm()
        form.full_clean()
        self.assertTrue(form.is_valid())

