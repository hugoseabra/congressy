"""
    Testes de models
"""
from test_plus.test import TestCase

from addon import models, rules
from addon.tests.mock_factory import MockFactory


class ModelsConfiguredTest(TestCase):
    """ Testes de configuração de afiliação. """

    def test_has_rules(self):
        # Session
        self.assertIn(
            rules.MustDateEndAfterDateStart,
            models.Session.rule_instances
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


class ManageOptionalCostFlagTest(TestCase):
    """
        Testes de manupilação da flag 'has_cost' do Optional vinculado ao
        Price.
    """
    mocker = None

    def setUp(self):
        self.mocker = MockFactory()

    def test_new_product_price_activate_optional_flag(self):
        """
            Testa se ao criar um ProductPrice a flag 'has_cost' de
            OptionalProduct torna-se "True"
        """
        optional = self.mocker.fake_optional_product()
        self.assertFalse(optional.has_cost)

        self.mocker.fake_product_price(optional_product=optional)

        # Agora has_cost é True
        self.assertTrue(optional.has_cost)

    def test_new_service_price_activate_optional_flag(self):
        """
            Testa se ao criar um ServicePrice a flag 'has_cost' de
            OptionalService torna-se "True"
        """
        optional = self.mocker.fake_optional_service()
        self.assertFalse(optional.has_cost)

        self.mocker.fake_service_price(optional_service=optional)

        # Agora has_cost é True
        self.assertTrue(optional.has_cost)

    def test_remove_product_price_deactivate_optional_flag(self):
        """
            Testa se ao excluir um ProductPrice e for não houver outros
            ProductPrices vinculados ao OptionalProduct, a flag 'has_cost' de
            OptionalProduct torna-se "False"
        """
        optional = self.mocker.fake_optional_product()
        price = self.mocker.fake_product_price(optional_product=optional)

        # Agora has_cost é True
        self.assertTrue(optional.has_cost)

        price.delete()

        # Agora has_cost is False
        self.assertFalse(optional.has_cost)

    def test_remove_service_price_deactivate_optional_flag(self):
        """
            Testa se ao excluir um ServicePrice e for não houver outros
            ServicePrices vinculados ao OptionalService, a flag 'has_cost' de
            OptionalService torna-se "False"
        """
        optional = self.mocker.fake_optional_service()
        price = self.mocker.fake_service_price(optional_service=optional)

        # Agora has_cost é True
        self.assertTrue(optional.has_cost)

        price.delete()

        # Agora has_cost is False
        self.assertFalse(optional.has_cost)
