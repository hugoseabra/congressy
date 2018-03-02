"""
     Partners Form tests
"""
from django.test import TestCase

from partner.forms import PartnerForm
from partner.tests.mocks import MockFactory


class PartnerFormTest(TestCase):
    """ Partner Form test implementation """

    def setUp(self):
        self.mock_factory = MockFactory()
        self.person = self.mock_factory._create_fake_person()

    def test_regular_form_validation(self):
        form = PartnerForm(data={'person': self.person.uuid})
        form.full_clean()
        self.assertTrue(form.is_valid())

