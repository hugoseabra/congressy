"""
    Testing the Option model form
"""

from django.utils.text import slugify
from test_plus.test import TestCase

from survey.managers import OptionManager
from survey.models import Question, Option
from survey.tests import MockFactory


class OptionManagerTest(TestCase):
    """ Main test implementation """

    def setUp(self):
        self.faker = MockFactory()
        self.survey = self.faker.fake_survey()
        self.question = self.faker.fake_question(survey=self.survey,
                                                 type=Question.FIELD_SELECT)

    def test_option_of_selectable_question(self):
        """
            Testa se opção é de um campo com suporte a opções.

            Conforme a regra:
                - Deve sempre ser de uma pergunta que suporte opções:
                    SELECT, RADIO ou CHECKBOX;
        """

        # Correct
        selectables = [
            Question.FIELD_SELECT,
            Question.FIELD_RADIO_GROUP,
            Question.FIELD_CHECKBOX_GROUP
        ]

        for question_type in selectables:
            selectable_question = self.faker.fake_question(
                survey=self.survey,
                type=question_type,
            )

            correct_form = OptionManager(
                data={
                    'question': selectable_question.pk,
                    'name': ' '.join(self.faker.fake_factory.words(nb=3)),
                    'value': ' '.join(self.faker.fake_factory.words(nb=2)),
                },
            )

            self.assertTrue(correct_form.is_valid())
            correct_form.save()

        # Incorrect
        for question_type in Question.TYPES:
            if question_type in selectables:
                continue

            non_selectable_question = self.faker.fake_question(
                survey=self.survey,
                type=question_type,
            )

            incorrect_form = OptionManager(
                data={
                    'question': non_selectable_question.pk,
                    'name': ' '.join(self.faker.fake_factory.words(nb=3)),
                    'value': ' '.join(self.faker.fake_factory.words(nb=2)),
                },
            )

            self.assertFalse(incorrect_form.is_valid())

    def test_setting_an_intro_option_as_first(self):
        """
            Testa se a regra:
                - Deve ser possível definir uma opção como "intro" que define
                  o primeiro  pergunta em branco

            está validando.
        """
        manager = OptionManager(
            data={
                'question': self.question.pk,
                'name': 'Intro Option',
            },
        )

    def test_same_option_same_question_with_prefix(self):
        """
            Testa se opção com um valor repetido na pergunta é salva com sucesso
            inserindo um prefixo e mantendo a unicidade.
        """

        option_text = "Random Option."

        og_slug = slugify(option_text)

        Option.objects.create(
            question=self.question,
            name=option_text,
            value=og_slug,
        )

        form1 = OptionManager(
            data={
                'question': self.question.pk,
                'name': option_text,
                'value': option_text,
            },
        )

        self.assertTrue(form1.is_valid())
        option1 = form1.save()
        self.assertEqual(option1.value, og_slug + "-1")

    def test_many_same_option_same_question_with_prefix_(self):
        """
            Testa se opção com um valor repetido na pergunta é salva com sucesso
            inserindo um prefixo e mantendo a unicidade em multiplos casos.
        """

        option_text = "Random Option."

        og_slug = slugify(option_text)

        Option.objects.create(
            question=self.question,
            name=option_text,
            value=og_slug,
        )

        for x in range(1, 6):
            Option.objects.create(
                question=self.question,
                name=option_text,
                value=og_slug + '-' + str(x),
            )

        form1 = OptionManager(
            data={
                'question': self.question.pk,
                'name': option_text,
                'value': option_text,
            },
        )

        self.assertTrue(form1.is_valid())
        option1 = form1.save()
        self.assertEqual(option1.value, og_slug + "-6")

        all_options = Option.objects.filter(
            question=self.question,
        )

        self.assertIs(all_options.count(), 7)
        self.assertEqual(all_options.first().value, og_slug)

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
