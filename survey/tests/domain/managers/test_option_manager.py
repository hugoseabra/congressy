"""
    Testing the Option model form
"""

from django.utils.text import slugify
from test_plus.test import TestCase

from survey.managers import OptionManager
from survey.models import Question
from survey.tests import MockFactory


class OptionManagerTest(TestCase):
    """ Main test implementation """

    def setUp(self):
        self.faker = MockFactory()
        self.survey = self.faker.fake_survey()
        self.question = self.faker.fake_question(survey=self.survey,
                                                 type=Question.FIELD_SELECT)

    def test_same_option_same_question_with_prefix(self):
        """
        Testa se opção com um valor repetido na pergunta é salva com sucesso
        inserindo um prefixo e mantendo a unicidade.
        """
        option_name = "Random Option."
        og_slug = slugify(option_name)
        value = 42
        form1 = OptionManager(
            data={
                'question': self.question.pk,
                'name': option_name,
                'value': str(value),
            },
        )

        form2 = OptionManager(
            data={
                'question': self.question.pk,
                'name': option_name,
                'value': str(value + 1),
            },
        )

        form3 = OptionManager(
            data={
                'question': self.question.pk,
                'name': option_name,
                'value': str(value + 2),
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

    def test_same_option_different_question_no_prefix(self):
        """
        Testa se opção com um nome repetido na pergunta é salva com sucesso
        inserindo um prefixo e mantendo a unicidade.
        """
        option_name = "Random Option."
        og_slug = slugify(option_name)
        value = 42

        type = Question.FIELD_SELECT

        question1 = self.question
        question2 = self.faker.fake_question(survey=self.survey, type=type)
        question3 = self.faker.fake_question(survey=self.survey, type=type)

        form1 = OptionManager(
            data={
                'question': question1.pk,
                'name': option_name,
                'value': str(value),
            },
        )

        form2 = OptionManager(
            data={
                'question': question2.pk,
                'name': option_name,
                'value': str(value + 1),
            },
        )

        form3 = OptionManager(
            data={
                'question': question3.pk,
                'name': option_name,
                'value': str(value + 2),
            },
        )

        self.assertTrue(form1.is_valid())
        form1.save()
        self.assertTrue(form2.is_valid())
        form2.save()
        self.assertTrue(form3.is_valid())
        form3.save()

        self.assertEqual(form1.instance.name, og_slug)
        self.assertEqual(form2.instance.name, og_slug)
        self.assertEqual(form3.instance.name, og_slug)

    def test_option_of_selectable_question(self):
        """ Testa se opção é de um campo com suporte a opções. """

        selectable_question = self.faker.fake_question(
            survey=self.survey,
            type=Question.FIELD_SELECT,
        )

        non_selectable_question = self.faker.fake_question(
            survey=self.survey,
            type=Question.FIELD_INPUT_TEXT,
        )

        correct_form = OptionManager(
            data={
                'question': selectable_question.pk,
                'name': "Correct Form",
                'value': "41",
            },
        )

        self.assertTrue(correct_form.is_valid())
        correct_form.save()

        incorrect_form = OptionManager(
            data={
                'question': non_selectable_question.pk,
                'name': "Incorrect Form",
                'value': "42",
            },
        )

        self.assertFalse(incorrect_form.is_valid())
