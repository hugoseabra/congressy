"""
    Testes para o Serviço de aplicação de Questionários.
"""

from test_plus.test import TestCase

from survey.models import Survey
from survey.services import SurveyService


class SurveyServiceTest(TestCase):
    """
        Implementação principal do test.
    """

    def test_survey_service_creation(self):
        """
            Testa a criação de questionários através do serviço de aplicação.
        """
        # Service é responsável para abstrair toda complexidade.
        service = SurveyService()

        # Objeto de questionário com suporte a todas as ações
        survey = service.create(
            name='Meu questionário',
            description='Formulário exemplo'
        )

        self.assertIsInstance(survey, Survey)
        self.assertIsNotNone(survey.pk)
