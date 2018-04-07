"""
    Testing the Answer model entity
"""

from django.forms import ValidationError
from test_plus.test import TestCase

from survey.models import Answer, Question
from survey.models.answer import SameSurveyRule
from survey.tests import MockFactory
from survey.models.mixins import RuleIntegrityError


class AnswerModelTest(TestCase):
    """ Main test implementation """

    def setUp(self):
        self.faker = MockFactory()
        self.survey = self.faker.fake_survey()
        self.question = self.faker.fake_question(self.survey,
                                                 type=Question.FIELD_SELECT)
        self.option = self.faker.fake_option(self.question)
        self.author = self.faker.fake_author(survey=self.survey)

    def test_answer_entity_cleaning(self):
        """
            Tests cleaning(validation) of the answer entity.
            validating the SameSurvey rule.
        """
        different_survey = self.faker.fake_survey()
        question_with_different_survey = self.faker.fake_question(
            survey=different_survey)

        answer = Answer(
            question=question_with_different_survey,
            value=self.option.value,
            author=self.author,
        )

        with self.assertRaises(ValidationError) as e:
            answer.clean()
            self.assertEqual(
                str(e.msg), 'A pergunta e o autor não pertencem ao mesmo '
                            'questionário.')

        # Correct answer cleaning just for peace of mind.
        new_answer = Answer(
            question=self.question,
            value=self.option.value,
            author=self.author,
        )

        new_answer.clean()
        new_answer.save()
        self.assertIsInstance(new_answer, Answer)

    def test_answer_SameSurveyRule_checker(self):
        checker = SameSurveyRule()

        # Test passando com o author e pergunta do mesmo survey.
        checker.question = self.question
        checker.author = self.author

        checker.check()

        # Teste falhando com author e pergunta com diferentes surveys.
        new_survey = self.faker.fake_survey()
        new_author = self.faker.fake_author(survey=new_survey)

        checker.question = self.question
        checker.author = new_author

        with self.assertRaises(RuleIntegrityError):
            checker.check()
