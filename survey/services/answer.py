"""
    Serviço de Aplicação para Respostas
"""

from survey.managers import AnswerManager
from survey.services import mixins


class AnswerService(mixins.ApplicationServiceMixin):
    """ Application Service """
    manager_class = AnswerManager
