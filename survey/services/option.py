"""
    Serviço de Aplicação para Opções
"""

from survey.managers import OptionManager
from survey.services import mixins


class OptionService(mixins.ApplicationServiceMixin):
    """ Application Service """
    manager_class = OptionManager
