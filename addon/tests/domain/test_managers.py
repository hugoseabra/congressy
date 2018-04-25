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


class SessionPersistenceTest(ManagerPersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""
    manager_class = managers.SessionManager
    required_fields = ('date_start', 'date_end',)
    data_edit_to = {
        'restrict_unique': True,
    }

    def setUp(self):

        date_start = datetime.now() - timedelta(days=3)
        date_end = datetime.now() + timedelta(days=3)

        self.data = {
            'date_start': date_start.strftime('%d/%m/%Y %H:%M'),
            'date_end': date_end.strftime('%d/%m/%Y %H:%M'),
            'restrict_unique': False,
        }

    def test_create(self):
        self.create()

    def test_edit(self):
        self.edit()


class OptionalProductManagerPersistenceTest(ManagerPersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""

    manager_class = managers.OptionalProductManager
    required_fields = (
        'name',
        'optional_type',
        'lot_categories',
        'session',
        'description',
        'quantity',
        'published',
        'has_cost',
    )

    data_edit_to = {
        'description': 'edited description',
        'quantity': random.randint(5, 10000),
        'published': False,
        'has_cost': False,
        'modified_by': 'test user',
    }

    def setUp(self):
        fake_factory = MockFactory()
        self.data = {
            'name': 'optional name',
            'optional_type': fake_factory.fake_optional_type().pk,
            'session': fake_factory.fake_session().pk,
            'lot_categories': (fake_factory.fake_lot_category().pk,),
            'description': 'original description',
            'quantity': 3,
            'published': True,
            'has_cost': True,
        }

    def _create_manager(self, instance=None, data=None):

        if not data:
            data = self.data

        if 'lot_categories' not in data:
            data['lot_categories'] = (self.fake_factory.fake_lot_category(

            ).pk,)

        if 'optional_type' not in data:
            data[
                'optional_type'] = self.fake_factory.fake_optional_type().pk

        if instance is not None:
            manager = self.manager_class(instance=instance, data=data)
        else:
            manager = self.manager_class(data=data)

        return manager

    def test_create(self):
        self.create()

    def test_edit(self):
        self.edit()


class OptionalProductPriceManagerRulesTest(TestCase):
    """Testes com a intenção de validar as regras dos managers normalmente
    colocadas dentro dos cleans"""

    def setUp(self):
        self.fake_factory = MockFactory()

    def test_setting_optional_product_has_cost_to_true(self):
        """ Regra: se tiver "prices", o campo has_cost deve ser True """
        new_optional_product = self.fake_factory.fake_optional_product()

        # Validando que o produto possui a flag correta
        self.assertFalse(new_optional_product.has_cost)

        date_start = datetime.now() - timedelta(days=3)
        date_end = datetime.now() + timedelta(days=3)

        price_manager = managers.ProductPriceManager(
            data={
                'lot_category': new_optional_product.lot_categories.first().pk,
                'date_start': date_start.strftime('%d/%m/%Y %H:%M'),
                'date_end': date_end.strftime('%d/%m/%Y %H:%M'),
                'price': format(decimal.Decimal(42.42), '.2f'),
                'optional_product': new_optional_product.pk,
            }
        )

        self.assertTrue(price_manager.is_valid())

        # Buscando o objeto OptionalProduct da persistência para validar se
        # o flag foi definido corretamente.

        persisted = addon_models.OptionalProduct.objects.get(
            pk=new_optional_product.pk)
        # Validando que o produto possui a flag correta
        self.assertTrue(persisted.has_cost)

    def test_setting_optional_service_has_cost_to_true(self):
        """ Regra: se tiver "prices", o campo has_cost deve ser True """
        new_optional_service = self.fake_factory.fake_optional_service()

        # Validando que o produto possui a flag correta
        self.assertFalse(new_optional_service.has_cost)

        date_start = datetime.now() - timedelta(days=3)
        date_end = datetime.now() + timedelta(days=3)

        price_manager = managers.ServicePriceManager(
            data={
                'lot_category': new_optional_service.lot_categories.first().pk,
                'date_start': date_start.strftime('%d/%m/%Y %H:%M'),
                'date_end': date_end.strftime('%d/%m/%Y %H:%M'),
                'price': format(decimal.Decimal(42.42), '.2f'),
                'optional_service': new_optional_service.pk,
            }
        )

        self.assertTrue(price_manager.is_valid())

        # Buscando o objeto OptionalProduct da persistência para validar se
        # o flag foi definido corretamente.

        persisted = addon_models.OptionalService.objects.get(
            pk=new_optional_service.pk)
        # Validando que o produto possui a flag correta
        self.assertTrue(persisted.has_cost)


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


class OptionalServiceManagerPersistenceTest(ManagerPersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""

    manager_class = managers.OptionalServiceManager
    required_fields = (
        'name',
        'session',
        'optional_type',
        'lot_categories',
        'description',
        'quantity',
        'published',
        'has_cost',
        'theme'
    )

    date_start = datetime.now() - timedelta(days=3)
    date_end = datetime.now() + timedelta(days=3)

    data_edit_to = {
        'description': 'edited description',
        'quantity': random.randint(5, 10000),
        'published': False,
        'has_cost': True,
        'modified_by': 'test user',
    }

    def setUp(self):
        fake_factory = MockFactory()

        self.data = {
            'name': 'optional name',
            'optional_type': fake_factory.fake_optional_type().pk,
            'session': fake_factory.fake_session().pk,
            'lot_categories': (fake_factory.fake_lot_category().pk,),
            'description': 'original description',
            'quantity': 3,
            'published': True,
            'has_cost': True,
            'theme': fake_factory.fake_theme().pk
        }

    def _create_manager(self, instance=None, data=None):

        if not data:
            data = self.data

        if 'lot_categories' not in data:
            data['lot_categories'] = (self.fake_factory.fake_lot_category(

            ).pk,)

        if 'optional_type' not in data:
            data[
                'optional_type'] = self.fake_factory.fake_optional_type().pk

        if 'theme' not in data:
            data['theme'] = self.fake_factory.fake_theme().pk

        if instance is not None:
            manager = self.manager_class(instance=instance, data=data)
        else:
            manager = self.manager_class(data=data)

        return manager

    def test_create(self):
        self.create()

    def test_edit(self):
        self.edit()


class ProductPriceManagerPersistenceTest(ManagerPersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""
    manager_class = managers.ProductPriceManager
    required_fields = (
        'optional_product',
        'lot_category',
        'date_start',
        'date_end',
        'price',
    )

    data_edit_to = {
        'price': decimal.Decimal(random.randrange(155, 389)) / 100,
    }

    def setUp(self):
        fake_factory = MockFactory()

        date_start = datetime.now()
        date_end = date_start + timedelta(days=15)

        optional = fake_factory.fake_optional_product()

        self.data = {
            'optional_product': optional.pk,
            'date_start': date_start.strftime("%d/%m/%Y %H:%M"),
            'date_end': date_end.strftime("%d/%m/%Y %H:%M"),
            'price': decimal.Decimal(random.randrange(155, 389)) / 100,
            'lot_category': optional.lot_categories.first().pk,
        }

    def test_create(self):
        self.create()

    def test_edit(self):
        self.edit()


class ServicePriceManagerPersistenceTest(ManagerPersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""
    manager_class = managers.ServicePriceManager
    required_fields = (
        'optional_service',
        'lot_category',
        'date_start',
        'date_end',
        'price',
    )

    data_edit_to = {
        'price': decimal.Decimal(random.randrange(155, 389)) / 100,
    }

    def setUp(self):
        fake_factory = MockFactory()

        date_start = datetime.now()
        date_end = date_start + timedelta(days=15)

        optional = fake_factory.fake_optional_service()

        self.data = {
            'optional_service': optional.pk,
            'date_start': date_start.strftime("%d/%m/%Y %H:%M"),
            'date_end': date_end.strftime("%d/%m/%Y %H:%M"),
            'price': decimal.Decimal(random.randrange(155, 389)) / 100,
            'lot_category': optional.lot_categories.first().pk,
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
