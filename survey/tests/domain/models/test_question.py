"""
    Testing the Question model entity
"""

from django.db import transaction
from django.db.utils import IntegrityError
from test_plus.test import TestCase

from survey.models import Question
from survey.tests import MockFactory


class QuestionModelTest(TestCase):
    """ Question model test """

    def setUp(self):
        self.fake_factory = MockFactory()
        self.survey = self.fake_factory.fake_survey()
        self.author = self.fake_factory.fake_author(survey=self.survey)

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

    def test_question_has_options(self):
        """
            Testa se a propriedade do model "has_options" está retornando o
            numero correto de opções vinculadas a pergunta.
        """

        question = Question(
            survey=self.survey,
            type=Question.FIELD_SELECT,
            label='label #1',
            name="Question #1",
            help_text='Some kind of help_text',
        )
        question.save()

        # Cria três opções vinculadas a essa pergunta
        for _ in range(3):
            self.fake_factory.fake_option(question=question)

        self.assertTrue(question.has_options)

    def test_question_has_answers(self):
        """
            Testa se a propriedade do model "has_options" está retornando o
            numero correto de opções vinculadas a pergunta.
        """

        """ Continue from here"""

        question = Question(
            survey=self.survey,
            type=Question.FIELD_SELECT,
            label='label #1',
            name="Question #1",
            help_text='Some kind of help_text',
        )
        question.save()

        self.assertFalse(question.has_options)

        # Cria três opções vinculadas a essa pergunta
        for _ in range(3):
            self.fake_factory.fake_answer(question=question,
                                          author=self.author)

        question = Question.objects.get(pk=question.pk)

        self.assertTrue(question.has_options)


class QuestionManagerTest(TestCase):
    """
        Question Manager test
    """

    def setUp(self):
        self.fake_factory = MockFactory()
        self.survey = self.fake_factory.fake_survey()

    def test_question_manager_next_order(self):
        question_name = self.fake_factory.fake_factory.words(nb=3)
        instance = Question.objects.create(
            survey=self.survey,
            type=Question.FIELD_INPUT_TEXT,
            label=question_name,
            name=question_name,
            help_text='Some kind of help_text',
        )
        self.assertIs(instance.order, 1)
        self.assertIs(Question.objects.next_order(self.survey), 2)

    def test_question_on_creation_ordering(self):
        """
            Testa se o manager está entregando a ordem correta, e se a
            atualização de ordens está funcionando.
        """

        for i in range(5):
            question_name = self.fake_factory.fake_factory.words(nb=3)
            question = Question(
                survey=self.survey,
                type=Question.FIELD_INPUT_TEXT,
                label=question_name,
                name=question_name,
                help_text='Some kind of help_text',
            )

            question.save()

        self.assertIs(Question.objects.first().order, 1)
        self.assertIs(Question.objects.last().order, 5)
