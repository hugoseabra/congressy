"""
    Serviço de Aplicação para Autores
"""

from survey.managers import AuthorManager
from survey.services import mixins


class AuthorService(mixins.ApplicationServiceMixin):
    """ Application Service """
    manager_class = AuthorManager
