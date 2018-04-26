""" Testes de services. """
import decimal
from datetime import datetime, timedelta

from addon import services
from base.tests.test_suites import \
    ApplicationServicePersistenceTestCase as TestCase
from ..mock_factory import MockFactory


class ThemeServicePersistenceTest(TestCase):
    """ Testes de persistência de dados: criação e edição."""
    application_service_class = services.ThemeService
    required_fields = ('name',)
    data_edit_to = {
        'name': 'another name edited',
    }

    def setUp(self):
        self.data = {
            'name': 'theme name',
        }

    def test_create(self):
        self.create()

    def test_edit(self):
        self.edit()


class OptionalTypeServicePersistenceTest(TestCase):
    """ Testes de persistência de dados: criação e edição."""
    application_service_class = services.OptionalTypeService
    required_fields = ('name',)
    data_edit_to = {
        'name': 'another name edited',
    }

    def setUp(self):
        self.data = {
            'name': 'theme name',
        }

    def test_create(self):
        self.create()

    def test_edit(self):
        self.edit()


class ProductServicePersistenceTest(TestCase):
    """ Testes de persistência de dados: criação e edição."""
    application_service_class = services.ProductService
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


class ServiceServicePersistenceTest(TestCase):
    """ Testes de persistência de dados: criação e edição."""
    application_service_class = services.ServiceService
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


class SubscriptionProductServicePersistenceTest(TestCase):
    """ Testes de persistência de dados: criação e edição."""
    application_service_class = services.SubscriptionProductService
    required_fields = (
        'subscription',
        'optional',
    )

    def setUp(self):
        fake_factory = MockFactory()
        self.event = fake_factory.fake_event()
        self.lot_category = fake_factory.fake_lot_category(event=self.event)
        self.lot = fake_factory.fake_lot(lot_category=self.lot_category,
                                         event=self.event)
        self.data = {
            'subscription': fake_factory.fake_subscription(lot=self.lot).pk,
            'optional': fake_factory.fake_product(
                lot_category=self.lot_category).pk,
        }

    def _create_service(self, instance=None, data=None):

        if not data:
            data = self.data

        fake_factory = MockFactory()

        if not data:
            data = {}

        if 'subscription' not in data:
            data['subscription'] = fake_factory.fake_subscription(
                lot=self.lot).pk

        if 'optional' not in data:
            data['optional'] = fake_factory.fake_product(
                lot_category=self.lot_category).pk

        if instance is not None:
            service = self.application_service_class(
                instance=instance,
                data=data
            )
        else:
            service = self.application_service_class(data=data)

        return service

    def test_create(self):
        self.create()

    def test_edit(self):
        self.data = None
        self.edit()


class SubscriptionServiceServicePersistenceTest(TestCase):
    """ Testes de persistência de dados: criação e edição."""
    application_service_class = services.SubscriptionServiceService
    required_fields = (
        'subscription',
        'optional',
    )

    def setUp(self):
        fake_factory = MockFactory()
        self.event = fake_factory.fake_event()
        self.lot_category = fake_factory.fake_lot_category(event=self.event)
        self.lot = fake_factory.fake_lot(lot_category=self.lot_category,
                                         event=self.event)
        self.data = {
            'subscription': fake_factory.fake_subscription(lot=self.lot).pk,
            'optional': fake_factory.fake_service(
                lot_category=self.lot_category).pk,
        }

    def _create_service(self, instance=None, data=None):

        if not data:
            data = self.data

        fake_factory = MockFactory()

        if not data:
            data = {}

        if 'subscription' not in data:
            data['subscription'] = fake_factory.fake_subscription(
                lot=self.lot).pk

        if 'optional' not in data:
            data['optional'] = fake_factory.fake_service(
                lot_category=self.lot_category).pk

        if instance is not None:
            service = self.application_service_class(
                instance=instance,
                data=data
            )
        else:
            service = self.application_service_class(data=data)

        return service

    def test_create(self):
        self.create()

    def test_edit(self):
        self.data = None
        self.edit()
