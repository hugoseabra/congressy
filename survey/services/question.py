"""
    Serviço de Aplicação para Perguntas
"""

from survey.managers import QuestionManager
from survey.services import mixins


class QuestionService(mixins.ApplicationServiceMixin):
    """ Application Service """
    manager_class = QuestionManager
