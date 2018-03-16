"""
    Testing the Answer Manager
"""

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

    def test_existing_answer_retrieval(self):
        """
            Testa se o manager consegue resgatar uma instancia que já existe.
        """

        existing_answer = Answer.objects.create(
            value='Uma resposta.',
            question=self.question,
            author=self.author,
        )

        found = AnswerManager._retrieve_author_answer(question=self.question,
                                                      author=self.author)

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
                   possuir o mesmo survey.

        """

        # Criando uma instancia pra ser ser usada para interagir via o manager.
        Answer.objects.create(
            value="Winter is coming.",
            question=self.question,
            author=self.author,
        )

        # Criando um novo survey para validar a regra de igualdade de surveys.
        new_survey = self.faker.fake_survey()\

        # Criando um novo autor com o novo survey para validar a regra de
        # igualdade de surveys.
        new_author_with_new_survey = self.faker.fake_author(survey=new_survey)

        # Criando um novo autor para validar a regra de igualdade de autores.
        new_author = self.faker.fake_author(survey=self.survey)


        non_identical_surveys_manager = AnswerManager(
            data={
                'value': 'Uma resposta.',
                'question': self.question.pk,
                'author': new_author_with_new_survey.pk,
            },
        )

        self.assertFalse(non_identical_surveys_manager.is_valid())
