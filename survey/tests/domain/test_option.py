"""
    Testing the Option model entity
"""

from test_plus.test import TestCase

from survey.models import Option
from survey.tests import MockFactory


class OptionModelTest(TestCase):
    """ Main test implementation """

    def setUp(self):
        self.fake_factory = MockFactory()
        self.survey = self.fake_factory.fake_survey()
        self.question = self.fake_factory.fake_question(survey=self.survey)

    def test_option_creation(self):
        option = Option(
            name='Test Option',
            value='15',
            question=self.question,
        )
        option.save()
        self.assertIsNotNone(option)
