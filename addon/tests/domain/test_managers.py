""" Testes de managers do módulo de opcionais. """

import decimal
import random
from datetime import datetime, timedelta

from test_plus.test import TestCase

from addon import models as addon_models, managers
from addon.tests.mock_factory import MockFactory
from base.tests.test_suites import ManagerPersistenceTestCase


class ThemeManagerPersistenceTest(ManagerPersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""
    manager_class = managers.ThemeManager
    required_fields = ('name',)
    data_edit_to = {
        'name': 'another name edited',
    }

    def setUp(self):
        self.data = {
            'name': 'my name',
        }

    def test_create(self):
        self.create()

    def test_edit(self):
        self.edit()


class OptionalTypePersistenceTest(ManagerPersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""
    manager_class = managers.OptionalTypeManager
    required_fields = ('name',)
    fake_factory = None

    data_edit_to = {
        'name': 'edited name',
    }

    def setUp(self):
        self.fake_factory = MockFactory()
        self.data = {
            'name': 'original name',
        }

    def test_create(self):
        self.create()

    def test_edit(self):
        self.edit()


class ProductManagerPersistenceTest(ManagerPersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""

    edited_date_start = datetime.now() - timedelta(days=6)
    edited_date_end = datetime.now() + timedelta(days=6)

    manager_class = managers.ProductManager
    required_fields = (
        'optional_type',
        'lot_category',
        'date_start',
        'date_end',
        'published',
        'created_by',
        'modified_by',
        'price',
        'restrict_unique',
        'description',
        'quantity',
    )

    data_edit_to = {
        'name': 'edited optional name',
        'published': True,
        'created_by': 'test edited user',
        'modified_by': 'test edited user',
        'price': round(decimal.Decimal(43.43), 2),
        'restrict_unique': True,
        'description': 'Optional edited description',
        'quantity': 10,
    }

    def _create_manager(self, instance=None, data=None):

        static_fake_factory = MockFactory()

        if not data:
            data = self.data

        if 'optional_type' not in data:
            data[
                'optional_type'] = static_fake_factory.fake_optional_type().pk

        if 'lot_category' not in data:
            data['lot_category'] = static_fake_factory.fake_lot_category().pk

        if instance is not None:
            manager = self.manager_class(instance=instance, data=data)
        else:
            manager = self.manager_class(data=data)

        return manager

    def setUp(self):
        fake_factory = MockFactory()
        date_start = datetime.now() - timedelta(days=3)
        date_end = datetime.now() + timedelta(days=3)
        self.data = {
            'optional_type': fake_factory.fake_optional_type().pk,
            'lot_category': fake_factory.fake_lot_category().pk,
            'name': 'optional name',
            'date_start': date_start.strftime('%d/%m/%Y %H:%M'),
            'date_end': date_end.strftime('%d/%m/%Y %H:%M'),
            'published': True,
            'created_by': 'test user',
            'modified_by': 'test user',
            'price': format(decimal.Decimal(42.42), '.2f'),
            'restrict_unique': False,
            'description': 'Optional description',
            'quantity': 5,
        }

    def test_create(self):
        self.create()

    def test_edit(self):
        self.edit()


class SubscriptionOptionalProductManagerRulesTest(TestCase):
    """Testes com a intenção de validar as regras dos managers normalmente
    colocadas dentro dos cleans"""
    fake_factory = None

    def setUp(self):
        self.fake_factory = MockFactory()

    def test_max_quantity_reached(self):
        """
            Testando a seguinte regra: Se quantidade de
            inscrições já foi atingida, novas inscrições não poderão ser
            realizadas
        """

        subscription = self.fake_factory.fake_subscription()
        failing_subscription = self.fake_factory.fake_subscription(
            lot=subscription.lot)

        lot_category = subscription.lot.category

        optional_product = self.fake_factory.fake_optional_product(
            lot_categories=(lot_category,),
        )
        optional_product.quantity = 1
        optional_product.save()

        price = self.fake_factory.fake_product_price(
            lot_category=lot_category,
            optional_product=optional_product
        )

        product_manager = managers.SubscriptionOptionalProductManager(
            data={
                'subscription': subscription.pk,
                'optional_product': optional_product.pk,
                'price': price.price,
            }
        )

        self.assertTrue(product_manager.is_valid())
        product_manager.save()
        self.assertEqual(
            addon_models.SubscriptionOptionalProduct.objects.all().count(), 1)

        failing_product_manager = managers.SubscriptionOptionalProductManager(
            data={
                'subscription': failing_subscription.pk,
                'optional_product': optional_product.pk,
                'price': price.price,
            }
        )

        self.assertFalse(failing_product_manager.is_valid())
        self.assertIn(
            'Quantidade de inscrições já foi atingida, novas inscrições não'
            ' poderão ser realizadas',
            failing_product_manager.errors['__all__']
        )


class SubscriptionOptionalServiceManagerRulesTest(TestCase):
    """Testes com a intenção de validar as regras dos managers normalmente
    colocadas dentro dos cleans"""
    fake_factory = None

    def setUp(self):
        self.fake_factory = MockFactory()

    def test_max_quantity_reached(self):
        """
            Testando a seguinte regra: Se quantidade de
            inscrições já foi atingida, novas inscrições não poderão ser
            realizadas
        """

        subscription = self.fake_factory.fake_subscription()
        failing_subscription = self.fake_factory.fake_subscription(
            lot=subscription.lot)

        lot_category = subscription.lot.category

        optional_service = self.fake_factory.fake_optional_service(
            lot_categories=(lot_category,),
        )
        optional_service.quantity = 1
        optional_service.save()

        price = self.fake_factory.fake_service_price(
            lot_category=lot_category,
            optional_service=optional_service
        )

        service_manager = managers.SubscriptionOptionalServiceManager(
            data={
                'subscription': subscription.pk,
                'optional_service': optional_service.pk,
                'price': price.price,
            }
        )

        self.assertTrue(service_manager.is_valid())
        service_manager.save()
        self.assertEqual(
            addon_models.SubscriptionOptionalService.objects.all().count(),
            1
        )

        failing_product_manager = managers.SubscriptionOptionalServiceManager(
            data={
                'subscription': failing_subscription.pk,
                'optional_service': optional_service.pk,
                'price': price.price,
            }
        )

        self.assertFalse(failing_product_manager.is_valid())
        self.assertIn(
            'Quantidade de inscrições já foi atingida, novas inscrições não'
            ' poderão ser realizadas',
            failing_product_manager.errors['__all__']
        )

    def test_validation_by_session_with_flag_on(self):
        # Crie uma única Subscription para ser usada para criar o
        # SubscriptionOptionalService
        subscription = self.fake_factory.fake_subscription()

        # Definindo datas conflitantes, ambas começam ao mesmo tempo.
        session = self.fake_factory.fake_session()
        now = datetime.now()

        session.date_start = now
        session.date_end = now + timedelta(days=1)

        # Configurando os dois serviços para usar a flag de sessão
        session.restrict_unique = True
        session.save()

        # Crie dois OptionalServices
        service_1 = self.fake_factory.fake_optional_service(
            lot_categories=(subscription.lot.category,), session=session)
        service_2 = self.fake_factory.fake_optional_service(
            lot_categories=(subscription.lot.category,), session=session)

        # Criando os gerenciadores de serviços
        service_1_manager = managers.SubscriptionOptionalServiceManager(
            data={
                'subscription': subscription.pk,
                'optional_service': service_1.pk,
                'price': format(decimal.Decimal(42.42), '.2f'),
            }
        )

        service_2_manager = managers.SubscriptionOptionalServiceManager(
            data={
                'subscription': subscription.pk,
                'optional_service': service_2.pk,
                'price': format(decimal.Decimal(42.42), '.2f'),
            }
        )

        # Validações
        self.assertTrue(service_1_manager.is_valid())
        service_1_manager.save()
        self.assertFalse(service_2_manager.is_valid())

    def test_validation_by_session_with_flag_off(self):
        # Crie uma única Subscription para ser usada para criar o
        # SubscriptionOptionalService
        subscription = self.fake_factory.fake_subscription()

        # Definindo datas conflitantes, ambas começam ao mesmo tempo.
        session = self.fake_factory.fake_session()
        now = datetime.now()

        session.date_start = now
        session.date_end = now + timedelta(days=1)

        # Configurando os dois serviços para usar a flag de sessão
        session.restrict_unique = False
        session.save()

        # Crie dois OptionalServices
        service_1 = self.fake_factory.fake_optional_service(
            lot_categories=(subscription.lot.category,), session=session)
        service_2 = self.fake_factory.fake_optional_service(
            lot_categories=(subscription.lot.category,), session=session)

        # Criando os gerenciadores de serviços
        service_1_manager = managers.SubscriptionOptionalServiceManager(
            data={
                'subscription': subscription.pk,
                'optional_service': service_1.pk,
                'price': format(decimal.Decimal(42.42), '.2f'),
            }
        )

        service_2_manager = managers.SubscriptionOptionalServiceManager(
            data={
                'subscription': subscription.pk,
                'optional_service': service_2.pk,
                'price': format(decimal.Decimal(42.42), '.2f'),
            }
        )

        # Validações
        self.assertTrue(service_1_manager.is_valid())
        service_1_manager.save()
        self.assertTrue(service_2_manager.is_valid())
        service_2_manager.save()

    def test_validation_by_theme_with_flag_on(self):
        # Crie uma única Subscription para ser usada para criar o
        # SubscriptionOptionalService
        subscription = self.fake_factory.fake_subscription()

        # Criando um tema e configurando seu limite para uma unica inscrição
        theme = self.fake_factory.fake_theme()
        theme.limit = 1
        theme.save()

        # Crie OptionalServices com tema.
        service = self.fake_factory.fake_optional_service(
            lot_categories=(subscription.lot.category,), theme=theme)

        # Criando os gerenciadores de serviços
        service_manager_1 = managers.SubscriptionOptionalServiceManager(
            data={
                'subscription': subscription.pk,
                'optional_service': service.pk,
                'price': format(decimal.Decimal(42.42), '.2f'),
            }
        )

        service_manager_2 = managers.SubscriptionOptionalServiceManager(
            data={
                'subscription': subscription.pk,
                'optional_service': service.pk,
                'price': format(decimal.Decimal(42.42), '.2f'),
            }
        )

        self.assertTrue(service_manager_1.is_valid())
        service_manager_1.save()
        self.assertFalse(service_manager_2.is_valid())

    def test_validation_by_theme_with_flag_off(self):
        # Crie uma única Subscription para ser usada para criar o
        # SubscriptionOptionalService
        subscription = self.fake_factory.fake_subscription()

        # Criando um tema e configurando seu limite como infinito
        theme = self.fake_factory.fake_theme()
        theme.limit = None
        theme.save()

        # Crie OptionalServices com tema.
        service = self.fake_factory.fake_optional_service(
            lot_categories=(subscription.lot.category,), theme=theme)

        # Criando os gerenciadores de serviços
        service_manager_1 = managers.SubscriptionOptionalServiceManager(
            data={
                'subscription': subscription.pk,
                'optional_service': service.pk,
                'price': format(decimal.Decimal(42.42), '.2f'),
            }
        )

        service_manager_2 = managers.SubscriptionOptionalServiceManager(
            data={
                'subscription': subscription.pk,
                'optional_service': service.pk,
                'price': format(decimal.Decimal(42.42), '.2f'),
            }
        )

        self.assertTrue(service_manager_1.is_valid())
        service_manager_1.save()
        self.assertTrue(service_manager_2.is_valid())
        service_manager_2.save()


class ServiceManagerPersistenceTest(ManagerPersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""

    edited_date_start = datetime.now() - timedelta(days=6)
    edited_date_end = datetime.now() + timedelta(days=6)

    manager_class = managers.ServiceManager
    required_fields = (
        'optional_type',
        'lot_category',
        'date_start',
        'date_end',
        'published',
        'created_by',
        'modified_by',
        'price',
        'restrict_unique',
        'description',
        'quantity',
        'theme',
        'place',
    )

    data_edit_to = {
        'name': 'edited optional name',
        'published': True,
        'created_by': 'test edited user',
        'modified_by': 'test edited user',
        'price': round(decimal.Decimal(43.43), 2),
        'restrict_unique': True,
        'description': 'Optional edited description',
        'quantity': 10,
        'place': 'Edited place',
    }

    def _create_manager(self, instance=None, data=None):

        static_fake_factory = MockFactory()

        if not data:
            data = self.data

        if 'optional_type' not in data:
            data[
                'optional_type'] = static_fake_factory.fake_optional_type().pk

        if 'lot_category' not in data:
            data['lot_category'] = static_fake_factory.fake_lot_category().pk

        if 'theme' not in data:
            data['theme'] = static_fake_factory.fake_theme().pk

        if instance is not None:
            manager = self.manager_class(instance=instance, data=data)
        else:
            manager = self.manager_class(data=data)

        return manager

    def setUp(self):
        fake_factory = MockFactory()
        date_start = datetime.now() - timedelta(days=3)
        date_end = datetime.now() + timedelta(days=3)
        self.data = {
            'optional_type': fake_factory.fake_optional_type().pk,
            'lot_category': fake_factory.fake_lot_category().pk,
            'name': 'optional name',
            'date_start': date_start.strftime('%d/%m/%Y %H:%M'),
            'date_end': date_end.strftime('%d/%m/%Y %H:%M'),
            'published': True,
            'created_by': 'test user',
            'modified_by': 'test user',
            'price': format(decimal.Decimal(42.42), '.2f'),
            'restrict_unique': False,
            'description': 'Optional description',
            'quantity': 5,
            'theme': fake_factory.fake_theme().pk,
            'place': 'Some place'
        }

    def test_create(self):
        self.create()

    def test_edit(self):
        self.edit()


class SubscriptionProductManagerPersistenceTest(ManagerPersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""

    manager_class = managers.SubscriptionOptionalProductManager
    required_fields = (
        'subscription',
        'price',
        'optional_product',
    )

    data_edit_to = {
        'price': decimal.Decimal(42),
    }
    fake_factory = None

    def setUp(self):
        self.fake_factory = MockFactory()
        subscription = self.fake_factory.fake_subscription()
        lot_category = subscription.lot.category

        optional = self.fake_factory.fake_optional_product(lot_categories=[
            lot_category
        ])

        self.data = {
            'optional_product': optional.pk,
            'subscription': subscription.pk,
            'price': decimal.Decimal(random.randrange(155, 389)) / 100,
        }

    def test_create(self):
        self.create()

    def test_edit(self):
        self.edit()


class SubscriptionServiceManagerPersistenceTest(ManagerPersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""

    manager_class = managers.SubscriptionOptionalServiceManager
    required_fields = (
        'subscription',
        'price',
        'optional_service',
    )

    data_edit_to = {
        'price': decimal.Decimal(42),
    }
    fake_factory = None

    def setUp(self):
        self.fake_factory = MockFactory()

        subscription = self.fake_factory.fake_subscription()
        lot_category = subscription.lot.category

        optional = self.fake_factory.fake_optional_service(lot_categories=[
            lot_category
        ])

        self.data = {
            'optional_service': optional.pk,
            'subscription': subscription.pk,
            'price': decimal.Decimal(random.randrange(155, 389)) / 100,
        }

    def test_create(self):
        self.create()

    def test_edit(self):
        self.edit()
