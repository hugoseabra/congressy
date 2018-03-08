"""
    Testing the Survey model entity
"""

from test_plus.test import TestCase

from survey.models import Survey
from survey.tests import MockFactory


class SurveyModelTest(TestCase):
    """ Main test implementation """

    def setUp(self):
        self.fake_factory = MockFactory()

    # Testing survey with zero question
    def test_survey_with_zero_questions_creation(self):

        survey = Survey(
            name="Simple Survey"
        )

        survey.save()
        self.assertIsNotNone(survey)
        self.assertEqual(0, survey.question_set.all().count())

    # Testing survey with one question
    def test_survey_with_one_questions_creation(self):

        survey = Survey(
            name="Simple Survey"
        )

        survey.save()
        self.assertIsNotNone(survey)

        self.fake_factory.fake_question(survey=survey)
        self.assertEqual(1, survey.question_set.all().count())

    # Testing survey with many questions
    def test_survey_with_multiple_questions_creation(self):

        survey = Survey(
            name="Simple Survey"
        )

        survey.save()
        self.assertIsNotNone(survey)
        for i in range(10):
            self.fake_factory.fake_question(survey=survey)

        self.assertEqual(10, survey.question_set.all().count())
