"""
    Testes de integridade de dados, para regras de domínio.
"""
from datetime import timedelta

from test_plus.test import TestCase

from addon import rules
from addon.tests.mock_factory import MockFactory
from base.models import RuleIntegrityError


class OptionalMustScheduleDateEndAfterDateStart(TestCase):
    """
        Testes de regras de opcionais onde a data de início deve antes da
        data de fim.
    """
    mocker = None
    rule = None

    def setUp(self):
        self.mocker = MockFactory()
        self.rule = rules.MustScheduleDateEndAfterDateStart()

    def test_optional_service_must_schedule_end_after_schedule_start(self):
        """
            Testa regra de opcional de serviço na qual data inicial antes da
            data final.
        """
        # Failure
        instance = self.mocker.fake_service()

        instance.schedule_end = instance.schedule_start - timedelta(days=3)

        with self.assertRaises(RuleIntegrityError) as e:
            self.rule.check(model_instance=instance)

        self.assertIn(
            'Data/hora inicial deve ser anterior a data/hora final',
            str(e.exception)
        )

        # Success
        instance = self.mocker.fake_service()
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

    def test_optional_service_unique_session(self):
        """
            Testa de optional não possui datas que podem ou não dar conflitar
            o horário.
        """
        rule = rules.ServiceMustHaveUniqueDatetimeScheduleInterval()

        # Failure
        # Já existe um preço será criado com o mesmo período
        optional1 = self.mocker.fake_service()

        optional2 = self.mocker.fake_service(
            lot_category=optional1.lot_category
        )

        # força mesmas datas
        optional2.schedule_start = optional1.schedule_start + timedelta(
            minutes=30)

        with self.assertRaises(RuleIntegrityError) as e:
            rule.check(model_instance=optional2)

        self.assertIn(
            'Conflito de horários de programação',
            str(e.exception)
        )

        # Sucesso
        optional2.schedule_start = optional1.schedule_end + timedelta(days=1)
        optional2.schedule_end = optional1.schedule_start + timedelta(days=3)

        rule.check(model_instance=optional2)


class OptionalServiceMustHaveSameEventAsTheme(TestCase):
    """
        Testes de regras de opcionais na qual o evento do serviço deve ser o
        mesmo evento do tema
    """
    mocker = None
    lot_category = None

    def setUp(self):
        self.mocker = MockFactory()
        self.lot_category = self.mocker.fake_lot_category()

    def test_optional_service_same_event_as_theme(self):
        """
            Testa de optional estar no mesmo evento que seu tema.
        """
        rule = rules.ThemeMustBeSameEvent()

        different_theme = self.mocker.fake_theme()

        optional = self.mocker.fake_service()
        optional.theme = different_theme

        with self.assertRaises(RuleIntegrityError) as e:
            rule.check(model_instance=optional)

        self.assertIn(
            'Conflito de evento entre o tema',
            str(e.exception)
        )

        # Sucesso
        correct_theme = self.mocker.fake_theme(
            event=optional.lot_category.event)
        optional.theme = correct_theme
        rule.check(model_instance=optional)


class OptionalMustHaveMinimumDaysTest(TestCase):
    """
        Testes de regras de opcionais na qual deve haver um opcional
        dentro de um mesmo horário (sessão) para a mesma categoria de lote
        de um evento.
    """
    mocker = None
    rule = None

    def setUp(self):
        self.mocker = MockFactory()
        self.rule = rules.OptionalMustHaveMinimumDays()

    def test_optional_product_minimum_days_test(self):
        """
            Testa de optional de produto salvo persiste 'release_days' com o
            o mínimo de dias configurado ou retorna um erro de integridade.
        """
        from addon import constants

        minimum_to_persist = constants.MINIMUM_RELEASE_DAYS - 1

        # Failure
        optional = self.mocker.fake_product()
        optional.release_days = minimum_to_persist

        with self.assertRaises(RuleIntegrityError) as e:
            self.rule.check(model_instance=optional)

        self.assertIn(
            'O número de dias de liberação de opcionais para inscrições não'
            ' confirmadas deve ser, no mínimo, "{}" dias'.format(
                constants.MINIMUM_RELEASE_DAYS
            ),
            str(e.exception)
        )

        # Sucesso
        optional.release_days = constants.MINIMUM_RELEASE_DAYS
        self.rule.check(model_instance=optional)

    def test_optional_service_minimum_days_test(self):
        """
            Testa de optional de serviço salvo persiste 'release_days' com o
            o mínimo de dias configurado ou retorna um erro de integridade.
        """
        from addon import constants

        minimum_to_persist = constants.MINIMUM_RELEASE_DAYS - 1

        # Failure
        optional = self.mocker.fake_service()
        optional.release_days = minimum_to_persist

        with self.assertRaises(RuleIntegrityError) as e:
            self.rule.check(model_instance=optional)

        self.assertIn(
            'O número de dias de liberação de opcionais para inscrições não'
            ' confirmadas deve ser, no mínimo, "{}" dias'.format(
                constants.MINIMUM_RELEASE_DAYS
            ),
            str(e.exception)
        )

        # Sucesso
        optional.release_days = constants.MINIMUM_RELEASE_DAYS
        self.rule.check(model_instance=optional)


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
