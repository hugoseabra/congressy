"""
    Serviço de Aplicação para Questionário
"""
from survey.managers import SurveyManager
from survey.services import mixins


class SurveyService(mixins.ApplicationServiceMixin):
    """ Implementação do Serviço de Aplicação de Questionários """
    manager_class = SurveyManager
