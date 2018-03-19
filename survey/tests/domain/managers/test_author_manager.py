"""
    Testing the Author Manager
"""

from test_plus.test import TestCase

from survey.managers import AuthorManager
from survey.tests import MockFactory


class AuthorManagerTest(TestCase):
    """ Main test implementation """

    def setUp(self):
        self.faker = MockFactory()
        self.survey = self.faker.fake_survey()
        self.question = self.faker.fake_question(survey=self.survey)
        self.person = self.faker.fake_person()

    def test_author_creation(self):
        """
            Test com a intenção de testar a criação de autores, com e sem
            usuarios.
        """

        author_with_user = AuthorManager(
            data={
                'name': self.faker.fake_factory.name(),
                'survey': self.survey.pk,
            },
            user=self.person.user.pk,
        )

        self.assertTrue(author_with_user.is_valid())

        # Validando que survey não pode ter dois autores.
        new_survey = self.faker.fake_survey()

        author_with_no_user = AuthorManager(
            data={
                'name': self.faker.fake_factory.name(),
                'survey': new_survey.pk,
            },
        )

        self.assertTrue(author_with_no_user.is_valid())

        # Testa salva pra ver que não alterou o nome do autor do nome do
        # usuario.
        author_with_user.save()
        self.assertEqual(author_with_user.instance.user,
                         self.person.user)

        # Validando a verificação de instancias e referencias no kwargs
        with self.assertRaises(TypeError):
            AuthorManager(
                data={
                    'name': self.faker.fake_factory.name(),
                },
                survey=self.survey.pk,
                user=None,
            )

    def test_author_creation_with_same_user_on_multiple_surveys(self):
        """
            Testa se o mesmo usuario consegue responder multiplos
            questionarios.
        """

        different_survey1 = self.faker.fake_survey()
        different_survey2 = self.faker.fake_survey()
        different_survey3 = self.faker.fake_survey()

        author1 = AuthorManager(
            data={
                'survey': different_survey1.pk
            },
            user=self.person.user,
        )
        author2 = AuthorManager(
            data={
                'survey': different_survey2.pk
            },
            user=self.person.user,
        )
        author3 = AuthorManager(
            data={
                'survey': different_survey3.pk
            },
            user=self.person.user,
        )

        self.assertTrue(author1.is_valid())
        self.assertTrue(author2.is_valid())
        self.assertTrue(author3.is_valid())

    def test_author_creation_different_survey(self):
        """
            Testa se a edição de autores respeita a regra de negocio para
            que um autor salvo em formulario não possa mudar de formulario
            na edição.
        """

        different_survey = self.faker.fake_survey()

        author = AuthorManager(
            data={
                'survey':self.survey.pk
            },
            user=self.person.user,
        )

        self.assertTrue(author.is_valid())
        author.save()

        author_edit = AuthorManager(
            data={
                'survey': different_survey.pk,
            },
            user=self.person.user,
            instance=author.instance,
        )

        self.assertFalse(author_edit.is_valid())
