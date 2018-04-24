"""
    Testes de integridade de dados, para regras de domínio.
"""
from test_plus.test import TestCase

from addon import models, rules


class ModelsConfiguredTest(TestCase):
    """ Testes de configuração de afiliação. """

    def test_has_rules(self):
        # Optional
        self.assertIn(
            rules.MustDateEndAfterDateStart,
            models.OptionalService.rule_instances
        )
        self.assertIn(
            rules.MustDateEndAfterDateStart,
            models.OptionalProduct.rule_instances
        )

        # Price
        self.assertIn(
            rules.MustDateEndAfterDateStart,
            models.ProductPrice.rule_instances
        )
        self.assertIn(
            rules.MustDateEndAfterDateStart,
            models.ServicePrice.rule_instances
        )

        self.assertIn(
            rules.MustLotCategoryBeAmongOptionalLotCategories,
            models.ProductPrice.rule_instances
        )
        self.assertIn(
            rules.MustLotCategoryBeAmongOptionalLotCategories,
            models.ServicePrice.rule_instances
        )

        self.assertIn(
            rules.MustHaveUniqueDatetimeInterval,
            models.ProductPrice.rule_instances
        )
        self.assertIn(
            rules.MustHaveUniqueDatetimeInterval,
            models.ServicePrice.rule_instances
        )

        # SubscriptionOptional
        self.assertIn(
            rules.MustBeSameOptionalLotCategory,
            models.SubscriptionOptionalProduct.rule_instances
        )
        self.assertIn(
            rules.MustBeSameOptionalLotCategory,
            models.SubscriptionOptionalService.rule_instances
        )
