"""
    Testing the Answer Manager
"""

from django import forms
from test_plus.test import TestCase

from survey.managers import AnswerManager
from survey.models import Answer
from survey.tests import MockFactory


class AnswerManagerTest(TestCase):
    """ Main test implementation """

    def setUp(self):
        self.faker = MockFactory()
        self.survey = self.faker.fake_survey()
        self.question = self.faker.fake_question(survey=self.survey)
        self.person = self.faker.fake_person()
        self.author = self.faker.fake_author(survey=self.survey)

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
            question=self.question,
            author=self.author,
        )

        self.assertTrue(new_answer.is_valid())
        new_answer.save()

        edited_answer = AnswerManager(
            data={
                'value': 'Uma resposta editada.',
            },
            question=self.question,
            author=self.author,
        )

        self.assertTrue(edited_answer.is_valid())
        edited_answer.save()

        self.assertNotEqual(edited_answer.instance.value,
                            new_answer.instance.value)
        self.assertEqual(edited_answer.instance.question,
                         new_answer.instance.question)
        self.assertEqual(edited_answer.instance.author,
                         new_answer.instance.author)

    def test_editing_same_answer_different_surveys(self):
        """
            Testa se a validação da regra de negocio é valida, em que,
            não pode ser feito uma edição de uma resposta a uma pergunta que
            não pertença ao formulario correto.
        """

        correct_answer = AnswerManager(
            data={
                'value': 'Uma resposta.',
            },
            question=self.question,
            author=self.author,
        )

        self.assertTrue(correct_answer.is_valid())
        correct_answer.save()

        persisted_instance = Answer.objects.get(question=self.question,
                                                author=self.author)

        diferente_survey = self.faker.fake_survey()
        diferente_question = self.faker.fake_question(survey=diferente_survey)

        wrong_answer = AnswerManager(
            data={
                'value': 'Uma resposta editada.',
            },
            instance=persisted_instance,
            question=diferente_question,
            author=self.author,
        )

        self.assertFalse(wrong_answer.is_valid())
        error_dict = wrong_answer.errors.as_data()
        error_list = list(error_dict)

        self.assertEqual(error_list[0], '__all__')
        self.assertIsInstance(error_dict['__all__'][0], forms.ValidationError)

        error_message = list(error_dict.values())[0][0].message
        self.assertEqual(error_message,
                         'Esta resposta não pertence a esta pergunta')
