"""
    Answer domain model.
    Resposta de um questionário, referente a uma pergunta a pertecente a um
    Autor.
"""
from django.forms import ValidationError

from survey.models.rule_checker import RuleChecker, RuleIntegrityError


class RuleInstanceTypeError(TypeError):
    """
    Exceção quando uma instância de regra de negócio de entidade informada
    mas não é instância de RuleChecker.
    """

    def __init__(self, message):
        self.message = 'Rule informado não é um RuleChecker: {}'.format(
            message)


class Entity(object):
    """
        Answer domain model implementation.
    """
    # Rule instances
    rule_instances = []

    def __init__(self, *args, **kwargs):

        checked_rules = []
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

    def _check_rules(self):
        """ Verifica as regras de integridade de domínio. """

        for rule in self.rule_instances:
            try:
                rule.check(self)
            except RuleIntegrityError as e:
                raise ValidationError(str(e))
