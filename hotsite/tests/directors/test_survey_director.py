"""
    Testa se a implementação de diretor de survey está agindo conforme
    especificado via as regras de negocio.
"""

from django.test import TestCase

from hotsite.directors import SurveyDirector
from hotsite.tests import MockFactory
from survey.forms import SurveyForm


class SurveyDirectorTest(TestCase):
    """
        Implementação do test;
    """

    def setUp(self):
        mock_factory = MockFactory()
        self.event = mock_factory.fake_event()
        self.survey = mock_factory.fake_survey()

        self.event_surveys = mock_factory.fake_event_survey(event=self.event,
                                                            survey=self.survey)
        self.user = mock_factory.fake_user()
        self.unused_user = mock_factory.fake_user()
        self.author = mock_factory.fake_author(user=self.user,
                                               survey=self.survey)
        self.questions = [mock_factory.fake_question(survey=self.survey) for
                          _ in range(3)]
        answers = []

        for question in self.questions:
            answers.append(mock_factory.fake_answer(question=question,
                                                    author=self.author))

        self.answers = answers

    def test_init(self):
        """
            Teste para validação da logica no construtor do diretor
        """

        # Test falhando
        with self.assertRaises(ValueError):
            event = 'não sou um evento, sou uma string'
            SurveyDirector(event=event, user=self.user)

        # Test passando
        self.assertIsInstance(SurveyDirector(event=self.event, user=self.user),
                              SurveyDirector)

    def test_get_forms_user_with_no_authorship(self):
        """
            Teste para validação do funcionamento do método 'get_forms'.

            Passar um usuario autenticado e que não possui nenhuma autoria
            deve retornar uma lista com um objeto mas sem dados
            iniciais('inital')

            Por que deve retornar só um? Só há um event_survey, mas há três
            perguntas dentro do survey em si.

        """
        director = SurveyDirector(event=self.event, user=self.unused_user)

        survey_forms_list = director.get_forms()

        self.assertIs(1, len(survey_forms_list))

        # Verificando que não há nada no initial.
        self.assertIs(0, len(survey_forms_list[0].initial))

    def test_get_forms_user_with_authorship(self):
        """
            Teste para validação do funcionamento do método 'get_forms'.

            Passar um usuario autenticado e que possui autoria de
            perguntas retornar uma lista  de objetos do tipo 'SurveyForm'
            este objeto que em si é uma instância de 'forms.Form'.

            Esses objetos da lista já devem vir 'populados' dentro do
            'inital' pois o usuário passado via parâmetro possui autoria de
            todas as três perguntas do formulário('survey').

        """

        # Verificando se de fato temos 3 perguntas
        self.assertIs(3, len(self.answers))

        director = SurveyDirector(event=self.event, user=self.user)

        survey_forms_list = director.get_forms()

        # Verificando que só temos uma instancia de event_survey
        self.assertIs(1, len(survey_forms_list))

        # Verificando que há 3 respostas no initial.
        self.assertIs(3, len(survey_forms_list[0].initial))

    def test_get_form_user_with_no_authorship(self):
        """
            Teste para validação do funcionamento do método 'get_form'.

            Chamar o método com um usuario deve retornar uma um objeto
            do tipo 'SurveyForm'

            Esse objeto não  deve vir 'populado' dentro do
            'inital' pois esse usuario não possui nenhuma autoria de nenhuma
            do formulário('survey') em questão.
        """

        director = SurveyDirector(event=self.event, user=self.unused_user)

        survey_form = director.get_form(survey=self.survey)

        self.assertIsInstance(survey_form, SurveyForm)

        # Verificando que não há nada no initial.
        self.assertIs(0, len(survey_form.initial))

    def test_get_form_user_with_authorship(self):
        """
            Teste para validação do funcionamento do método 'get_form'.

            Chamar o método com um usuario deve retornar uma um objeto
            do tipo 'SurveyForm'

            Esse objeto  deve vir 'populado' dentro do 'inital' pois esse
            usuario possui 3 autorias dentro deste  formulário('survey').
        """

        director = SurveyDirector(event=self.event, user=self.user)

        survey_form = director.get_form(survey=self.survey)

        self.assertIsInstance(survey_form, SurveyForm)

        # Verificando que há 3 respostas no initial.
        self.assertIs(3, len(survey_form.initial))
