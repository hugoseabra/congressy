"""
    Testing the Answer model entity
"""

from test_plus.test import TestCase

from survey.models import Answer, Question
from survey.tests import MockFactory


class AnswerModelTest(TestCase):
    """ Main test implementation """

    def setUp(self):
        self.faker = MockFactory()
        self.survey = self.faker.fake_survey()
        self.question = self.faker.fake_question(self.survey,
                                                 type=Question.FIELD_SELECT)
        self.option = self.faker.fake_option(self.question)
        self.author = self.faker.fake_author(survey=self.survey)

    def test_answer_with_human_display_when_selectable_question(self):
        """
        Testa se resposta de uma pergunta com suporte a opções sempre possui
        saída de valor para o usuário (human_display).
        """

        answer = Answer(
            question=self.question,
            value=self.option.value,
            author=self.author,
        )

        self.assertIsNotNone(answer._get_human_display())
        self.assertEqual(answer._get_human_display(), self.option.name)

        answer.save()

        self.assertIsNotNone(answer.human_display)
        self.assertEqual(answer.human_display, self.option.name)

