"""
    Testes de integridade de dados, para regras de domínio.
"""
from datetime import timedelta

from test_plus.test import TestCase

from addon import rules
from addon.tests.mock_factory import MockFactory
from base.models import RuleIntegrityError


class OptionalMustDateEndAfterDateStartTest(TestCase):
    """
        Testes de regras de opcionais onde a data de início deve antes da
        data de fim.
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
        instance = self.mocker.fake_service()

        instance.date_end = instance.date_start - timedelta(days=3)

        with self.assertRaises(RuleIntegrityError) as e:
            self.rule.check(model_instance=instance)

        self.assertIn(
            'Data inicial deve ser anterior a data final',
            str(e.exception)
        )

        # Success
        instance = self.mocker.fake_service()
        self.rule.check(model_instance=instance)

    def test_optional_product_must_date_end_after_date_start(self):
        """
            Testa regra de opcional de produto na qual data inicial antes da
            data final.
        """
        # Failure
        instance = self.mocker.fake_product()

        instance.date_end = instance.date_start - timedelta(days=3)

        with self.assertRaises(RuleIntegrityError) as e:
            self.rule.check(model_instance=instance)

        self.assertIn(
            'Data inicial deve ser anterior a data final',
            str(e.exception)
        )

        # Success
        instance = self.mocker.fake_product()
        self.rule.check(model_instance=instance)


class OptionalMustHaveUniqueDatetimeIntervalTest(TestCase):
    """
        Testes de regras de opcionais na qual deve haver um opcional
        dentro de um mesmo horário (sessão) para a mesma categoria de lote
        de um evento.
    """
    mocker = None
    lot_category = None

    def setUp(self):
        self.mocker = MockFactory()
        self.lot_category = self.mocker.fake_lot_category()

    def test_optional_product_unique_session(self):
        """
            Testa de optional não possui datas que podem ou não dar conflitar
            o horário.
        """
        rule = rules.ProductMustHaveUniqueDatetimeInterval()

        # Failure
        # Já existe um preço será criado com o mesmo período
        optional1 = self.mocker.fake_product()

        optional2 = \
            self.mocker.fake_product(
                lot_category=optional1.lot_category
            )

        # força mesmas datas
        optional2.date_start = optional1.date_start + timedelta(minutes=30)

        with self.assertRaises(RuleIntegrityError) as e:
            rule.check(model_instance=optional2)

        self.assertIn(
            'As datas informadas conflitam com outro(s) opcionais(s)',
            str(e.exception)
        )

        # Sucesso
        optional2.date_start = optional1.date_end + timedelta(days=1)
        optional2.date_end = optional1.date_start + timedelta(days=3)

        rule.check(model_instance=optional2)

    def test_optional_service_unique_session(self):
        """
            Testa de optional não possui datas que podem ou não dar conflitar
            o horário.
        """
        rule = rules.ServiceMustHaveUniqueDatetimeInterval()

        # Failure
        # Já existe um preço será criado com o mesmo período
        optional1 = self.mocker.fake_service()

        optional2 = \
            self.mocker.fake_service(
                lot_category=optional1.lot_category
            )

        # força mesmas datas
        optional2.date_start = optional1.date_start + timedelta(minutes=30)

        with self.assertRaises(RuleIntegrityError) as e:
            rule.check(model_instance=optional2)

        self.assertIn(
            'As datas informadas conflitam com outro(s) opcionais(s)',
            str(e.exception)
        )

        # Sucesso
        optional2.date_start = optional1.date_end + timedelta(days=1)
        optional2.date_end = optional1.date_start + timedelta(days=3)

        rule.check(model_instance=optional2)


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
