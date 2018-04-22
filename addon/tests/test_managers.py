""" Testes de managers do módulo de opcionais. """

import decimal

import random

from addon import managers
from base.tests.test_suites import ManagerPersistenceTestCase
from .mock_factory import MockFactory


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
            self.data['lot_category'] = self.fake_factory.fake_lot_category()

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
