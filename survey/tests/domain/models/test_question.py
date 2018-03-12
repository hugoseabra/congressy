"""
    Testing the Question model entity
"""

from django.db import transaction
from django.db.utils import IntegrityError
from test_plus.test import TestCase

from survey.models import Question
from survey.tests import MockFactory


class QuestionModelTest(TestCase):
    """ Main test implementation """

    def setUp(self):
        self.fake_factory = MockFactory()
        self.survey = self.fake_factory.fake_survey()

    def test_question_unique_in_survey(self):
        """ Testa se pergunta é única em um formulário. """

        name = "Question #1"

        question = Question(
            survey=self.survey,
            type=Question.FIELD_INPUT_TEXT,
            label='label #1',
            name=name,
            help_text='Some kind of help_text',
        )

        question.save()

        duplicate_question = Question(
            survey=self.survey,
            type=Question.FIELD_INPUT_TEXT,
            label='label #1',
            name=name,
            help_text='Some kind of help_text',
        )

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                duplicate_question.save()

        self.assertEqual(Question.objects.filter(name=name).count(), 1)

    def test_same_question_name_different_survey(self):
        survey1 = self.survey
        survey2 = self.fake_factory.fake_survey()

        question1 = Question(
            survey=survey1,
            type=Question.FIELD_INPUT_TEXT,
            label='label #1',
            name="Question #1",
            help_text='Some kind of help_text',
        )

        question2 = Question(
            survey=survey2,
            type=Question.FIELD_INPUT_TEXT,
            label='label #1',
            name="Question #1",
            help_text='Some kind of help_text',
        )
        with transaction.atomic():
            question1.save()
            question2.save()

        self.assertEqual(Question.objects.filter(name="Question #1").count(),
                         2)
