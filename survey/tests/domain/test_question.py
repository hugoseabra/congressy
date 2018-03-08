"""
    Testing the Question model entity
"""

from test_plus.test import TestCase

from survey.models import Question
from survey.tests import MockFactory


class QuestionModelTest(TestCase):
    """ Main test implementation """

    def setUp(self):
        self.fake_factory = MockFactory()
        self.survey = self.fake_factory.fake_survey()

    # Testing 'simple' question with zero options
    def test_zero_options_simple_question_creation(self):
        question = Question(
            name='Test Question',
            is_required=True,
            is_complex=False,
            survey=self.survey,
        )
        question.save()
        self.assertIsNotNone(question)
        self.assertFalse(question.is_complex)

    # Testing 'complex' question with one option
    def test_single_option_complex_question_creation(self):
        question = Question(
            name='Test Question',
            is_required=True,
            is_complex=True,
            survey=self.survey,
        )

        question.save()

        self.assertIsNotNone(question)
        self.assertTrue(question.is_complex)

        self.fake_factory.fake_option(question)

        self.assertEqual(question.option_set.all().count(), 1)

    # Testing 'complex' question with many options
    def test_multiple_option_complex_question_creation(self):
        question = Question(
            name='Test Question',
            is_required=True,
            is_complex=True,
            survey=self.survey,
        )

        question.save()

        self.assertIsNotNone(question)
        self.assertTrue(question.is_complex)

        for i in range(5):
            self.fake_factory.fake_option(question)

        self.assertEqual(question.option_set.all().count(), 5)
