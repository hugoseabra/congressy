""" Testes de managers do módulo de opcionais. """

import decimal
from datetime import datetime

import random

from addon import managers
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


class PriceManagerPersistenceTest(ManagerPersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""
    manager_class = managers.PriceManager
    required_fields = ('price', 'lot_category', 'release_days')

    data_edit_to = {
        'release_days': 42,
        'price': decimal.Decimal(random.randrange(155, 389)) / 100,
    }

    def _create_manager(self, instance=None, data=None):

        if not data:
            data = self.data

        if 'lot_category' not in data:
            data['lot_category'] = self.fake_factory.fake_lot_category()

        if instance is not None:
            manager = self.manager_class(instance=instance, data=data)
        else:
            manager = self.manager_class(data=data)

        return manager

    def setUp(self):

        self.fake_factory = MockFactory()
        self.data = {
            'release_days': 1,
            'price': decimal.Decimal(random.randrange(155, 389)) / 100,
            'lot_category': self.fake_factory.fake_lot_category().pk,
        }

    def test_create(self):
        self.create()

    def test_edit(self):
        self.edit()


class OptionalTypePersistenceTest(ManagerPersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""
    manager_class = managers.OptionalTypeManager
    required_fields = ('name',)

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

    def _create_manager(self, instance=None, data=None):

        if not data:
            data = self.data

        if 'lot_categories' not in data:
            data['lot_categories'] = (self.fake_factory.fake_lot_category(

            ).pk,)

        if 'optional_type' not in data:
            data['optional_type'] = self.fake_factory.fake_optional_type().pk

        if instance is not None:
            manager = self.manager_class(instance=instance, data=data)
        else:
            manager = self.manager_class(data=data)

        return manager

    def setUp(self):

        self.fake_factory = MockFactory()
        self.data = {
            'date_end': datetime(1990, 1, 1, 00, 00, 00),
            'description': 'original description',
            'quantity': 3,
            'published': True,
            'has_cost': True,
            'lot_categories': (self.fake_factory.fake_lot_category().pk,),
            'optional_type': self.fake_factory.fake_optional_type().pk,
        }

    def test_create(self):
        self.create()

    def test_edit(self):
        self.edit()


class OptionalServiceManagerPersistenceTest(ManagerPersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""

    manager_class = managers.OptionalServiceManager
    required_fields = (
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

    def _create_manager(self, instance=None, data=None):

        if not data:
            data = self.data

        if 'lot_categories' not in data:
            data['lot_categories'] = (self.fake_factory.fake_lot_category(

            ).pk,)

        if 'optional_type' not in data:
            data['optional_type'] = self.fake_factory.fake_optional_type().pk

        if 'theme' not in data:
            data['theme'] = self.fake_factory.fake_theme().pk

        if instance is not None:
            manager = self.manager_class(instance=instance, data=data)
        else:
            manager = self.manager_class(data=data)

        return manager

    def setUp(self):

        self.fake_factory = MockFactory()
        self.data = {
            'date_end': datetime(1990, 1, 1, 00, 00, 00),
            'description': 'original description',
            'quantity': 3,
            'published': True,
            'has_cost': True,
            'lot_categories': (self.fake_factory.fake_lot_category().pk,),
            'optional_type': self.fake_factory.fake_optional_type().pk,
            'start_on': datetime(1991, 1, 1, 00, 00, 00),
            'duration': 3,
            'theme': self.fake_factory.fake_theme().pk
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
