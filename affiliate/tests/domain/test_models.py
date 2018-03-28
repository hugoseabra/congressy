""" Testes de models do módulo de Afiliados. """

from test_plus.test import TestCase

from affiliate import rules
from affiliate.models import Affiliation


class ModelsConfiguredTest(TestCase):
    """ Testes de configuração de afiliação. """

    def test_has_rules(self):
        self.assertIn(
            rules.MustProvideMaxPercentAffiliationRule,
            Affiliation.rule_instances
        )

        self.assertIn(
            rules.MaxParticipationExceededAffiliationRule,
            Affiliation.rule_instances
        )
