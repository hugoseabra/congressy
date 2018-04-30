"""
    Testes de models
"""
from test_plus.test import TestCase

from addon import models, rules


class ModelsConfiguredTest(TestCase):
    """ Testes de configuração de afiliação. """

    def test_has_rules(self):
        # Optionals
        self.assertIn(
            rules.MustDateEndAfterDateStart,
            models.Product.rule_instances
        )
        self.assertIn(
            rules.MustDateEndAfterDateStart,
            models.Service.rule_instances
        )

        self.assertIn(
            rules.OptionalMustHaveMinimumDays,
            models.Product.rule_instances
        )
        self.assertIn(
            rules.OptionalMustHaveMinimumDays,
            models.Service.rule_instances
        )

        # Price
        self.assertIn(
            rules.MustDateEndAfterDateStart,
            models.Product.rule_instances
        )
        self.assertIn(
            rules.MustDateEndAfterDateStart,
            models.Service.rule_instances
        )

        # self.assertIn(
        #     rules.ProductMustHaveUniqueDatetimeInterval,
        #     models.Product.rule_instances
        # )
        # self.assertIn(
        #     rules.ServiceMustHaveUniqueDatetimeInterval,
        #     models.Service.rule_instances
        # )

        # SubscriptionOptional
        self.assertIn(
            rules.MustBeSameOptionalLotCategory,
            models.SubscriptionProduct.rule_instances
        )
        self.assertIn(
            rules.MustBeSameOptionalLotCategory,
            models.SubscriptionService.rule_instances
        )
