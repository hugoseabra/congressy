"""
    Testes de models
"""
from test_plus.test import TestCase

from addon import models, rules


class ModelsConfiguredTest(TestCase):
    """ Testes de configuração de afiliação. """

    def test_has_rules(self):
        # Optionals - Product
        self.assertIn(
            rules.RestrictSubscriptionAfterOptionalDateEnd,
            models.Service.rule_instances
        )

        self.assertIn(
            rules.OptionalMustHaveMinimumDays,
            models.Product.rule_instances
        )

        # Optionals - Service
        self.assertIn(
            rules.MustScheduleDateEndAfterDateStart,
            models.Service.rule_instances
        )

        self.assertIn(
            rules.ServiceMustHaveUniqueDatetimeScheduleInterval,
            models.Service.rule_instances
        )

        self.assertIn(
            rules.RestrictSubscriptionAfterOptionalDateEnd,
            models.Product.rule_instances
        )

        self.assertIn(
            rules.OptionalMustHaveMinimumDays,
            models.Service.rule_instances
        )

        # SubscriptionOptional
        self.assertIn(
            rules.MustBeSameOptionalLotCategory,
            models.SubscriptionProduct.rule_instances
        )

        self.assertIn(
            rules.MustBeSameOptionalLotCategory,
            models.SubscriptionService.rule_instances
        )
