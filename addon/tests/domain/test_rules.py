"""
    Testes de integridade de dados, para regras de domínio.
"""
from datetime import timedelta

from test_plus.test import TestCase

from addon import rules
from addon.tests.mock_factory import MockFactory
from base.models import RuleIntegrityError


class OptionalPriceRulesTest(TestCase):
    """
        Testes de regras de domínio de Opcional e Price.
    """
    mocker = None

    def setUp(self):
        self.mocker = MockFactory()
        self.rule = rules.MustDateEndAfterDateStart()

    def test_optional_service_must_date_end_after_date_start(self):
        """
            Testa regra de opcional de serviço na qual data inicial antes da
            data final.
        """
        # Failure
        instance = self.mocker.fake_optional_service()

        instance.date_end = instance.date_start - timedelta(days=3)

        with self.assertRaises(RuleIntegrityError) as e:
            self.rule.check(model_instance=instance)

        self.assertIn(
            'Data inicial deve ser anterior a data final',
            str(e.exception)
        )

        # Success
        instance = self.mocker.fake_optional_service()
        self.rule.check(model_instance=instance)

    def test_optional_product_must_date_end_after_date_start(self):
        """
            Testa regra de opcional de produto na qual data inicial antes da
            data final.
        """
        # Failure
        instance = self.mocker.fake_optional_product()

        instance.date_end = instance.date_start - timedelta(days=3)

        with self.assertRaises(RuleIntegrityError) as e:
            self.rule.check(model_instance=instance)

        self.assertIn(
            'Data inicial deve ser anterior a data final',
            str(e.exception)
        )

        # Success
        instance = self.mocker.fake_optional_product()
        self.rule.check(model_instance=instance)

    def test_service_price_must_date_end_after_date_start(self):
        """
            Testa regra de preço na qual data inicial antes da data final.
        """
        # Failure
        instance = self.mocker.fake_service_price()

        instance.date_end = instance.date_start - timedelta(days=3)

        with self.assertRaises(RuleIntegrityError) as e:
            self.rule.check(model_instance=instance)

        self.assertIn(
            'Data inicial deve ser anterior a data final',
            str(e.exception)
        )

        # Success
        instance = self.mocker.fake_service_price()
        self.rule.check(model_instance=instance)

    def test_product_price_must_date_end_after_date_start(self):
        """
            Testa regra de preço na qual data inicial antes da data final.
        """
        # Failure
        instance = self.mocker.fake_product_price()

        instance.date_end = instance.date_start - timedelta(days=3)

        with self.assertRaises(RuleIntegrityError) as e:
            self.rule.check(model_instance=instance)

        self.assertIn(
            'Data inicial deve ser anterior a data final',
            str(e.exception)
        )

        # Success
        instance = self.mocker.fake_product_price()
        self.rule.check(model_instance=instance)


class PriceRulesTest(TestCase):
    """
        Testes de regras de domínio de Rules de Price.
    """
    mocker = None
    lot_category = None
    product_price = None
    service_price = None

    def setUp(self):
        self.mocker = MockFactory()
        self.lot_category = self.mocker.fake_lot_category()
        self.product_price = self.mocker.fake_product_price()
        self.service_price = self.mocker.fake_service_price()

    def test_lot_category_must_be_in_optional_categories(self):
        """
            Testa regra de categoria de lote informa estar entre os
        """
        rule = rules.MustLotCategoryBeAmongOptionalLotCategories()
        original_lot_category = self.product_price.lot_category

        # Failure - ProductPrice
        price = self.product_price

        # Muda a categoria para uma que não está vinculada ao evento e
        # categoria de lote previament inseridos na instância de price.
        price.lot_category = self.lot_category

        with self.assertRaises(RuleIntegrityError) as e:
            rule.check(model_instance=price)

        self.assertIn(
            'Você deve informar uma categoria de lote que já esteja inserida'
            ' no opcional',
            str(e.exception)
        )

        # Success - ProductPrice
        price.lot_category = original_lot_category
        rule.check(model_instance=price)

        # Failure - ServicePrice
        original_lot_category = self.service_price.lot_category

        # Failure - ProductPrice
        price = self.service_price

        # Muda a categoria para uma que não está vinculada ao evento e
        # categoria de lote previament inseridos na instância de price.
        price.lot_category = self.lot_category

        with self.assertRaises(RuleIntegrityError) as e:
            rule.check(model_instance=price)

        self.assertIn(
            'Você deve informar uma categoria de lote que já esteja inserida'
            ' no opcional',
            str(e.exception)
        )

        # Success - ServicePrice
        price.lot_category = original_lot_category
        rule.check(model_instance=price)

    def test_unique_datetime_interval(self):
        """
            Testa de preço inserido em um opcional não possui datas que chocam
            entre si.
        """
        rule = rules.MustHaveUniqueDatetimeInterval()

        # Failure - ProductPrice
        price1 = self.product_price

        # Já existe um preço será criado com o mesmo período
        price2 = \
            self.mocker.fake_product_price(lot_category=price1.lot_category)

        # força mesmas datas
        price2.date_start = price1.date_start + timedelta(minutes=30)

        with self.assertRaises(RuleIntegrityError) as e:
            rule.check(model_instance=price2)

        self.assertIn(
            'As datas informadas conflitam com outro(s) preço(s)',
            str(e.exception)
        )

        # Sucesso - ProductPrice
        price2.date_start = price1.date_end + timedelta(days=1)
        price2.date_end = price2.date_start + timedelta(days=3)

        rule.check(model_instance=price2)

        # Failure - ServicePrice
        price1 = self.service_price

        # Já existe um preço será criado com o mesmo período
        price2 = \
            self.mocker.fake_service_price(lot_category=price1.lot_category)

        # força mesmas datas
        price2.date_start = price1.date_start + timedelta(minutes=30)

        with self.assertRaises(RuleIntegrityError) as e:
            rule.check(model_instance=price2)

        self.assertIn(
            'As datas informadas conflitam com outro(s) preço(s)',
            str(e.exception)
        )

        # Sucesso - ServicePrice
        price2.date_start = price1.date_end + timedelta(days=1)
        price2.date_end = price2.date_start + timedelta(days=3)

        rule.check(model_instance=price2)


class SubscriptionOptionalRulesTest(TestCase):
    """
        Testes de regras de domínio de Rules de Inscrição de Optional.
    """
    mocker = None
    lot_category = None
    rule = None

    def setUp(self):
        self.mocker = MockFactory()
        self.lot_category = self.mocker.fake_lot_category()
        self.rule = rules.MustBeSameOptionalLotCategory()

    def test_subscription_and_optional_service_same_lot_category(self):
        """
            Testa se inscrição e opcional são do mesma categoria de lote.
        """
        # Failure - SubscriptionOptionalService
        subscription_optional = \
            self.mocker.fake_subscription_optional_service()

        original_lot_category = \
            subscription_optional.subscription.lot.category

        # simula inscriçao de outra categoria
        subscription_optional.subscription.lot.category = self.lot_category

        with self.assertRaises(RuleIntegrityError) as e:
            self.rule.check(model_instance=subscription_optional)

        self.assertIn(
            'Você deve informar uma categoria de lote que já esteja inserida'
            ' no opcional',
            str(e.exception)
        )

        # Success - SubscriptionOptionalService
        # retorna para inscrição com o mesmo lot_category
        subscription_optional.subscription.lot.category = original_lot_category
        self.rule.check(model_instance=subscription_optional)

    def test_subscription_and_optional_product_same_lot_category(self):
        """
            Testa se inscrição e opcional são do mesma categoria de lote.
        """
        # Failure - SubscriptionOptionalProduct
        subscription_optional = \
            self.mocker.fake_subscription_optional_product()

        original_lot_category = \
            subscription_optional.subscription.lot.category

        # simula inscriçao de outra categoria
        subscription_optional.subscription.lot.category = self.lot_category

        with self.assertRaises(RuleIntegrityError) as e:
            self.rule.check(model_instance=subscription_optional)

        self.assertIn(
            'Você deve informar uma categoria de lote que já esteja inserida'
            ' no opcional',
            str(e.exception)
        )

        # Success - SubscriptionOptionalProduct
        # retorna para inscrição com o mesmo lot_category
        subscription_optional.subscription.lot.category = original_lot_category
        self.rule.check(model_instance=subscription_optional)
