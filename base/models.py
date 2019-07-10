"""
    Survey module domain models
"""
from abc import ABC, abstractmethod

from django.db.utils import IntegrityError
from django.forms import ValidationError
from django.utils.safestring import mark_safe

__all__ = ['EntityMixin', 'RuleChecker', 'RuleIntegrityError']


class RuleIntegrityError(IntegrityError):
    """
    Exceção erro durante verificação de integridade de entidade de domínio.
    """
    pass


class RuleInstanceTypeError(TypeError):
    """
    Exceção quando uma instância de regra de negócio de entidade informada
    mas não é instância de RuleChecker.
    """

    def __init__(self, message):
        self.message = 'Rule informado não é um RuleChecker: {}'.format(
            message)


class RuleChecker(ABC):
    """
    Classe concreta de implementação de verficação de integridade de domínio
    de uma entidade.
    :raise RuleIntegrityError
    """

    @abstractmethod
    def check(self, model_instance, *args, **kwargs):  # pragma: no cover
        pass


class EntityMixin(object):
    """
        Answer domain model implementation.
    """
    # Rule instances
    rule_instances = dict()

    def __init__(self, *args, **kwargs):

        checked_rules = list()
        for rule in self.rule_instances:
            if isinstance(rule, RuleChecker) or issubclass(rule, RuleChecker):
                checked_rules.append(rule)
                continue

            raise RuleInstanceTypeError(rule.__class__)

        if checked_rules:
            self.rule_instances = checked_rules

        super().__init__(*args, **kwargs)

    def clean(self):
        self._check_rules()

    def is_new(self):
        return self._state.adding is True

    def _check_rules(self):
        """ Verifica as regras de integridade de domínio. """

        for rule in self.rule_instances:
            if not isinstance(rule, RuleChecker):
                rule = rule()

            try:
                rule.check(self)
            except RuleIntegrityError as e:
                raise ValidationError(mark_safe(str(e)))
