"""
    Testing the Answer Manager
"""

from django import forms
from test_plus.test import TestCase

from survey.managers import AnswerManager
from survey.models import Answer
from survey import constants
from survey.tests import MockFactory


class AnswerManagerTest(TestCase):
    """ Main test implementation """

    def setUp(self):
        self.faker = MockFactory()
        self.survey = self.faker.fake_survey()
        self.question = self.faker.fake_question(survey=self.survey,
                                                 type=constants.FIELD_SELECT)
        self.person = self.faker.fake_person()
        self.author = self.faker.fake_author(survey=self.survey)

    def test_existing_answer_retrieval(self):
        """
            Testa se o manager consegue resgatar uma instancia que já existe.
        """

        existing_answer = Answer.objects.create(
            value='Uma resposta.',
            question=self.question,
            author=self.author,
        )

        found = AnswerManager._retrieve_author_answer(
            question_id=self.question.pk,
            author_id=self.author.pk,
        )

        self.assertIsNotNone(found)
        self.assertIsInstance(found, Answer)
        self.assertEqual(found, existing_answer)

    def test_answer_manager_creation(self):
        """
            Testa a criação de um manager de respostas
        """

        manager = AnswerManager(
            data={
                'value': 'Uma resposta.',
                'question': self.question.pk,
                'author': self.author.pk,
            },
        )

        self.assertTrue(manager.is_valid())
        manager.save()

    def test_answer_editing_without_instance(self):
        """
            Testa se o usuário, ao submeter resposta de um formulário que ele
            já tenha respondido anteriormente, possui a resposta anterior
            editada, não gerando nova resposta sem passar uma instancia previa.
        """

        new_answer = AnswerManager(
            data={
                'value': 'Uma resposta.',
                'question': self.question.pk,
                'author': self.author.pk,
            },
        )

        self.assertTrue(new_answer.is_valid())
        new_answer.save()

        edited_answer = AnswerManager(
            data={
                'value': 'Uma resposta editada.',
                'question': self.question.pk,
                'author': self.author.pk,
            },
        )

        self.assertTrue(edited_answer.is_valid())
        edited_answer.save()

        # Verificando que o valor das respostas foi editado
        self.assertNotEqual(edited_answer.instance.value,
                            new_answer.instance.value)

        # Verificando que a resposta continua sendo a mesma.
        self.assertEqual(edited_answer.instance.question,
                         new_answer.instance.question)

        # Verificando que o author continua sendo o mesmo.
        self.assertEqual(edited_answer.instance.author,
                         new_answer.instance.author)

    def test_answer_editing_with_instance(self):
        """
            Testa se o usuário, ao submeter resposta de um formulário que ele
            já tenha respondido anteriormente, possui a resposta anterior
            editada, não gerando nova resposta passando uma instancia previa.
        """

        new_answer_value = 'Uma resposta.'
        edited_answer_value = 'Uma resposta editada.'

        new_answer = AnswerManager(
            data={
                'value': new_answer_value,
                'question': self.question.pk,
                'author': self.author.pk,
            },
        )

        self.assertTrue(new_answer.is_valid())
        new_answer.save()

        edited_answer = AnswerManager(
            data={
                'value': edited_answer_value,
                'question': self.question.pk,
                'author': self.author.pk,
            },
            instance=new_answer.instance,
        )

        # Verificando que as instancias são as mesmas.
        self.assertEqual(edited_answer.instance.pk, new_answer.instance.pk)

        # Validando e persistindo a resposta.
        self.assertTrue(edited_answer.is_valid())
        edited_answer.save()

        # Verificando que o valor das respostas foi editado
        self.assertNotEqual(edited_answer.instance.value,
                            new_answer_value)

        # Verificando que a pergunta continua sendo a mesma.
        self.assertEqual(edited_answer.instance.question,
                         new_answer.instance.question)

        # Verificando que o author continua sendo o mesmo.
        self.assertEqual(edited_answer.instance.author,
                         new_answer.instance.author)

    def test_answer_cleaning_author(self):
        """
            Testa se a regra de negocio que é validada apenas em
            caso de edição de respostas conforme especificada dentro do
            clean de autores:

              - Author passado via instancia e autor passado via dados devem
                  ser do mesmo questionario.

              - Author passado via instancia e autor passado via dados devem
                  possuir a mesma pergunta.

        """

        # Criando uma instancia pra ser ser usada para interagir via o manager.
        instance = Answer.objects.create(
            value="Winter is coming.",
            question=self.question,
            author=self.author,
        )

        # Criando um novo survey para validar a regra de igualdade de surveys.
        new_survey = self.faker.fake_survey()
        diferente_survey_author = self.faker.fake_author(survey=new_survey)

        non_identical_surveys_manager = AnswerManager(
            data={
                'value': 'Uma resposta.',
                'question': self.question.pk,
                'author': diferente_survey_author.pk,
            },
            instance=instance,
        )
        #
        self.assertFalse(non_identical_surveys_manager.is_valid())
        error_dict = non_identical_surveys_manager.errors.as_data()
        self.assertIsInstance(error_dict['author'][0],
                              forms.ValidationError)
        self.assertEqual(error_dict['author'][0].message,
                         'A pergunta e o autor não pertencem ao mesmo '
                         'questionário')

        # Criando uma nova pergunta para testar a regra de igualdade de
        # perguntas.
        new_question = self.faker.fake_question(self.survey)

        # Testando que Author passado via instancia e autor passado via dados
        # devem possuir a mesma pergunta.
        non_identical_questions_manager = AnswerManager(
            data={
                'value': 'Uma resposta.',
                'question': new_question.pk,
                'author': self.author.pk,
            },
            instance=instance,
        )

        self.assertFalse(non_identical_questions_manager.is_valid())

        error_dict = non_identical_questions_manager.errors.as_data()
        self.assertIsInstance(error_dict['author'][0],
                              forms.ValidationError)
        self.assertEqual(error_dict['author'][0].message,
                         'A resposta não pertence a este autor')

    def test_answer_cleaning_set_human_display_com_option(self):
        """
            Testa se o metodo clean está setando o campo 'human_display'
            corretamente na existencia de options na pergunta.
        """

        # Criando uma instancia de option.
        created_option = self.faker.fake_option(self.question)

        manager = AnswerManager(
            data={
                'value': created_option.value,
                'question': self.question.pk,
                'author': self.author.pk,
            },
        )

        self.assertTrue(manager.is_valid())

        answer = manager.save()

        self.assertEqual(answer.human_display, created_option.name)

    def test_answer_cleaning_set_human_display_sem_option(self):
        """
            Testa se o metodo clean está setando o campo 'human_display'
            corretamente sem opções vinculadas a pergunta
        """

        value = 'Um valor qualquer'

        manager = AnswerManager(
            data={
                'value': value,
                'question': self.question.pk,
                'author': self.author.pk,
            },
        )

        self.assertTrue(manager.is_valid())

        answer = manager.save()

        self.assertEqual(answer.human_display, value)
