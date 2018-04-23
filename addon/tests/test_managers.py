""" Testes de managers do módulo de opcionais. """

import decimal
from datetime import datetime, timedelta

import random

from addon import managers
from base.tests.test_suites import ManagerPersistenceTestCase
from .mock_factory import MockFactory


def gen_random_datetime(min_year=1900, max_year=datetime.now().year):
    # generate a datetime in format yyyy-mm-dd hh:mm:ss.000000
    start = datetime(min_year, 1, 1, 00, 00, 00)
    years = max_year - min_year + 1
    end = start + timedelta(days=365 * years)
    return start + (end - start) * random.random()


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

    temp_faker = MockFactory()
    event = temp_faker.fake_event()
    lot_category = temp_faker.fake_lot_category(event=event)
    print(lot_category.pk)
    print(event.name)
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
