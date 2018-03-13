"""
    Testing the Answer Manager
"""

from test_plus.test import TestCase

from survey.managers import AnswerManager
from survey.tests import MockFactory


class AnswerManagerTest(TestCase):
    """ Main test implementation """

    def setUp(self):
        self.faker = MockFactory()
        self.survey = self.faker.fake_survey()
        self.question = self.faker.fake_question(survey=self.survey)
        self.person = self.faker.fake_person()

    def test_answer_unique_if_user(self):
        """
        Testa se o usuário, ao submeter resposta de um formulário que ele
        já tenha respondido anteriormente, possui a resposta anterior
        editada, não gerando nova resposta.
        """

        new_answer = AnswerManager(
            data={
                'value': 'Uma resposta.',
            },
            user=self.person.user,
            question=self.question,
        )

        self.assertTrue(new_answer.is_valid())
        new_answer.save()

        edited_answer = AnswerManager(
            data={
                'value': 'Uma resposta editada.',
            },
            user=self.person.user,
            question=self.question,
        )

        self.assertTrue(edited_answer.is_valid())
        edited_answer.save()

        self.assertNotEqual(edited_answer.instance.value,
                            new_answer.instance.value)
        self.assertEqual(edited_answer.instance.question,
                         new_answer.instance.question)
        self.assertEqual(edited_answer.instance.user, new_answer.instance.user)
