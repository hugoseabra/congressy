""" Testes de managers do módulo de opcionais. """

import decimal
from datetime import datetime, timedelta

import random
from test_plus.test import TestCase

from addon import managers, models as addon_models
from base.tests.test_suites import ManagerPersistenceTestCase
from .mock_factory import MockFactory, gen_random_datetime


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


class OptionalProductManagerPersistenceTest(ManagerPersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""

    manager_class = managers.OptionalProductManager
    required_fields = (
        'name',
        'date_start',
        'date_end',
        'description',
        'quantity',
        'published',
        'has_cost',
        'lot_categories',
        'optional_type',
    )

    data_edit_to = {
        'description': 'edited description',
        'date_end': gen_random_datetime(),
        'quantity': random.randint(5, 10000),
        'published': False,
        'has_cost': False,
        'modified_by': 'test user',
    }

    def setUp(self):

        date_start = datetime.now() - timedelta(days=3)
        date_end = datetime.now() + timedelta(days=3)

        fake_factory = MockFactory()
        self.data = {
            'name': 'optional name',
            'date_start': date_start.strftime('%d/%m/%Y %H:%M'),
            'date_end': date_end.strftime('%d/%m/%Y %H:%M'),
            'description': 'original description',
            'quantity': 3,
            'published': True,
            'has_cost': True,
            'lot_categories': (fake_factory.fake_lot_category().pk,),
            'optional_type': fake_factory.fake_optional_type().pk,
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


class OptionalServiceManagerPersistenceTest(ManagerPersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""

    manager_class = managers.OptionalServiceManager
    required_fields = (
        'name',
        'date_start',
        'date_end',
        'description',
        'quantity',
        'published',
        'has_cost',
        'lot_categories',
        'optional_type',
        'start_on',
        'duration',
        'theme'
    )

    data_edit_to = {
        'description': 'edited description',
        'date_end': gen_random_datetime(),
        'quantity': random.randint(5, 10000),
        'published': False,
        'has_cost': False,
        'modified_by': 'test user',
        'start_on': gen_random_datetime(),
        'duration': random.randint(5, 10000)
    }

    def setUp(self):

        date_start = datetime.now() - timedelta(days=3)
        date_end = datetime.now() + timedelta(days=3)

        fake_factory = MockFactory()

        self.data = {
            'name': 'optional name',
            'date_start': date_start.strftime('%d/%m/%Y %H:%M'),
            'date_end': date_end.strftime('%d/%m/%Y %H:%M'),
            'description': 'original description',
            'quantity': 3,
            'published': True,
            'has_cost': True,
            'lot_categories': (fake_factory.fake_lot_category().pk,),
            'optional_type': fake_factory.fake_optional_type().pk,
            'start_on': datetime(1991, 1, 1, 00, 00, 00),
            'duration': 3,
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

    def _create_manager(self, instance=None, data=None):

        fake_factory = MockFactory()

        if not data:
            data = self.data

        if 'lot_category' not in data:
            data['lot_category'] = fake_factory.fake_lot_category()

        if instance is not None:
            manager = self.manager_class(instance=instance, data=data)
        else:
            manager = self.manager_class(data=data)

        return manager

    def setUp(self):

        fake_factory = MockFactory()

        date_start = datetime.now()
        date_end = date_start + timedelta(days=15)

        self.data = {
            'optional_product': fake_factory.fake_optional_product().pk,
            'date_start': date_start.strftime("%d/%m/%Y %H:%M"),
            'date_end': date_end.strftime("%d/%m/%Y %H:%M"),
            'price': decimal.Decimal(random.randrange(155, 389)) / 100,
            'lot_category': fake_factory.fake_lot_category().pk,
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

    def _create_manager(self, instance=None, data=None):

        fake_factory = MockFactory()

        if not data:
            data = self.data

        if 'lot_category' not in data:
            data['lot_category'] = fake_factory.fake_lot_category()

        if instance is not None:
            manager = self.manager_class(instance=instance, data=data)
        else:
            manager = self.manager_class(data=data)

        return manager

    def setUp(self):

        fake_factory = MockFactory()

        date_start = datetime.now()
        date_end = date_start + timedelta(days=15)

        self.data = {
            'optional_service': fake_factory.fake_optional_service().pk,
            'date_start': date_start.strftime("%d/%m/%Y %H:%M"),
            'date_end': date_end.strftime("%d/%m/%Y %H:%M"),
            'price': decimal.Decimal(random.randrange(155, 389)) / 100,
            'lot_category': fake_factory.fake_lot_category().pk,
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
        'total_allowed',
        'optional_product',
    )

    data_edit_to = {
        'price': decimal.Decimal(42),
        'total_allowed': 42,
        'count': 3,
    }

    def _create_manager(self, instance=None, data=None):

        if not data:
            data = self.data

        if 'subscription' not in data:
            data['subscription'] = self.fake_factory.fake_subscription().pk

        if 'optional_product' not in data:
            data['optional_product'] = \
                self.fake_factory.fake_optional_product().pk

        if instance is not None:
            manager = self.manager_class(instance=instance, data=data)
        else:
            manager = self.manager_class(data=data)

        return manager

    def setUp(self):

        self.fake_factory = MockFactory()
        self.data = {
            'subscription': self.fake_factory.fake_subscription().pk,
            'optional_product': self.fake_factory.fake_optional_product().pk,
            'price': decimal.Decimal(random.randrange(155, 389)) / 100,
            'total_allowed': 3
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
        'total_allowed',
        'optional_service',
    )

    data_edit_to = {
        'price': decimal.Decimal(42),
        'total_allowed': 42,
        'count': 3,
    }

    def _create_manager(self, instance=None, data=None):

        if not data:
            data = self.data

        if 'subscription' not in data:
            data['subscription'] = self.fake_factory.fake_subscription().pk

        if 'optional_service' not in data:
            data['optional_service'] = \
                self.fake_factory.fake_optional_service().pk

        if instance is not None:
            manager = self.manager_class(instance=instance, data=data)
        else:
            manager = self.manager_class(data=data)

        return manager

    def setUp(self):

        self.fake_factory = MockFactory()
        self.data = {
            'subscription': self.fake_factory.fake_subscription().pk,
            'optional_service': self.fake_factory.fake_optional_service().pk,
            'price': decimal.Decimal(random.randrange(155, 389)) / 100,
            'total_allowed': 3
        }

    def test_create(self):
        self.create()

    def test_edit(self):
        self.edit()


class OptionalProductManagerRule(TestCase):
    """Testes com a intenção de validar as regras dos managers normalmente
    colocadas dentro dos cleans"""
    pass


class ProductPriceManagerRule(TestCase):
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
