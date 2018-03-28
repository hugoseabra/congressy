""" Testes de regras de negócios do módulo de Afiliados. """

from test_plus.test import TestCase

from affiliate import rules
from affiliate.models import Affiliation


class AffiliationRulesTest(TestCase):
    """ Testa regras de negócios do módulo de Afiliados. """

    def test_must_provide_max_percent(self):
        """
            Testa a configuração de limite máximo de percentual de uma
            afiliação.
        """
        rule = rules.MustProvideMaxPercentAffiliationRule()

        # Nenhum percentual configurado
        model_class = Affiliation
        model_class.AFFILIATE_MAX_PERCENTAGE = None

        instance = model_class()

        # FALHA: percentual deve ser configurado
        with self.assertRaises(rules.RuleIntegrityError):
            rule.check(model_instance=instance)

        # SUCESSO: configura percentual
        instance.AFFILIATE_MAX_PERCENTAGE = 15.5
        rule.check(model_instance=instance)

    def test_participaion_exceeded(self):
        """
        Testa afiliação com percentual acima do máximo permitido.
        """
        rule = rules.MaxParticipationExceededAffiliationRule()

        # Percentual de 20% que é acima de 15.5% permitido.
        instance = Affiliation(percent=20)
        instance.AFFILIATE_MAX_PERCENTAGE = 15.5

        # FALHA: percentual excedido
        with self.assertRaises(rules.RuleIntegrityError):
            rule.check(model_instance=instance)

        instance = Affiliation(percent=15.5)
        instance.AFFILIATE_MAX_PERCENTAGE = 15.5

        # SUCESSO: percentual dentro do limite
        rule.check(model_instance=instance)
