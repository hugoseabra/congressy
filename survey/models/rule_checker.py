"""
    Regras de integridade de entidade de domínio.
"""

from django.db.utils import IntegrityError
from abc import ABC, abstractmethod


class RuleIntegrityError(IntegrityError):
    """
    Exceção erro durante verificação de integridade de entidade de domínio.
    """
    pass


class RuleChecker(ABC):
    """
    Classe concreta de implementação de verficação de integridade de domínio
    de uma entidade.
    :raise RuleIntegrityError
    """
    @abstractmethod
    def check(self, entity_instance):  # pragma: no cover
        pass
