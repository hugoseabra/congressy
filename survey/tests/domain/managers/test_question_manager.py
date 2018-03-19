"""
    Testing the Question model form
"""

from test_plus.test import TestCase
from survey.managers import QuestionManager
from survey.models import Question
from survey.tests import MockFactory
from django.utils.text import slugify


class QuestionManagerTest(TestCase):
    """ Main test implementation """

    def setUp(self):
        self.fake_factory = MockFactory()
        self.survey = self.fake_factory.fake_survey()

    def test_question_manager_creation(self):
        """
            Testa a criação de um manager de perguntas
        """

        question_name = ' '.join(self.fake_factory.fake_factory.words(nb=2))

        manager = QuestionManager(
            data={
                'survey': self.survey.pk,
                'type': Question.FIELD_INPUT_TEXT,
                'name': question_name,
                'label': question_name,
            },
        )

        self.assertTrue(manager.is_valid())
        manager.save()

    def test_same_question_same_survey_with_prefix(self):
        """
        Testa se pergunta com um nome repetido no formulário é salvo com
        sucesso inserindo um prefixo e mantendo a unicidade.
        """

        question_name = "Random Question"
        og_slug = slugify(question_name)

        form1 = QuestionManager(
            data={
                'type': Question.FIELD_INPUT_TEXT,
                'name': question_name,
                'label': question_name,
                'survey': self.survey.pk,
            },
        )

        form2 = QuestionManager(
            data={
                'type': Question.FIELD_INPUT_TEXT,
                'name': question_name,
                'label': question_name,
                'survey': self.survey.pk,
            },
        )

        form3 = QuestionManager(
            data={
                'type': Question.FIELD_INPUT_TEXT,
                'name': question_name,
                'label': question_name,
                'survey': self.survey.pk,
            },
        )

        self.assertTrue(form1.is_valid())
        form1.save()
        self.assertTrue(form2.is_valid())
        form2.save()
        self.assertTrue(form3.is_valid())
        form3.save()

        self.assertEqual(form1.instance.name, og_slug)
        self.assertNotEqual(form2.instance.name, og_slug)
        self.assertNotEqual(form3.instance.name, og_slug)
        self.assertNotEqual(form3.instance.name, form2.instance.name)

    def test_same_question_different_survey_no_prefix(self):
        """
        Testa se perguntas com nomes repetidos em formulários diferentes é
        salvo com sucesso com o mesmo slug.
        """

        question_name = "Random Question"
        og_slug = slugify(question_name)

        survey1 = self.survey
        survey2 = self.fake_factory.fake_survey()

        form1 = QuestionManager(
            data={
                'survey': survey1.pk,
                'type': Question.FIELD_INPUT_TEXT,
                'name': question_name,
                'label': question_name,
            },
        )

        form2 = QuestionManager(
            data={
                'survey': survey2.pk,
                'type': Question.FIELD_INPUT_TEXT,
                'name': question_name,
                'label': question_name,
            },
        )

        self.assertTrue(form1.is_valid())
        form1.save()
        self.assertTrue(form2.is_valid())
        form2.save()

        self.assertEqual(form1.instance.name, og_slug)
        self.assertEqual(form2.instance.name, og_slug)
