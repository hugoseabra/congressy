""" Testes de services. """
import decimal
from datetime import datetime, timedelta

from test_plus.test import TestCase

from addon import models, services
from base.tests.test_suites import \
    ApplicationServicePersistenceTestCase as PersistenceTestCase
from ..mock_factory import MockFactory


class ThemeServicePersistenceTest(PersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""
    application_service_class = services.ThemeService
    required_fields = ('name', 'event')
    data_edit_to = {
        'name': 'another name edited',
    }

    def setUp(self):
        fake_factory = MockFactory()
        self.data = {
            'event': fake_factory.fake_event().pk,
            'name': 'theme name',
        }

    def _create_service(self, instance=None, data=None):
        if not data:
            data = self.data

        if 'event' not in data:
            data['event'] = MockFactory().fake_event().pk

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
        self.edit()


class OptionalProductTypeServicePersistenceTest(PersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""
    application_service_class = services.OptionalProductTypeService
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


class OptionalServiceTypeServicePersistenceTest(PersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""
    application_service_class = services.OptionalServiceTypeService
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


class ProductServicePersistenceTest(PersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""
    application_service_class = services.ProductService
    required_fields = (
        'optional_type',
        'lot_category',
        'date_end_sub',
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
        date_end = datetime.now() + timedelta(days=3)

        self.data = {
            'optional_type': fake_factory.fake_optional_product_type().pk,
            'lot_category': fake_factory.fake_lot_category().pk,
            'name': 'optional name',
            'date_end_sub': date_end.strftime('%d/%m/%Y %H:%M'),
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


class ServiceServicePersistenceTest(PersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""
    application_service_class = services.ServiceService
    required_fields = (
        'optional_type',
        'lot_category',
        'schedule_start',
        'schedule_end',
        'date_end_sub',
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
        lot_category = fake_factory.fake_lot_category()
        self.data = {
            'optional_type': fake_factory.fake_optional_service_type().pk,
            'lot_category': lot_category.pk,
            'name': 'optional name',
            'schedule_start': date_start.strftime('%d/%m/%Y %H:%M'),
            'schedule_end': date_end.strftime('%d/%m/%Y %H:%M'),
            'date_end_sub': date_end.strftime('%d/%m/%Y %H:%M'),
            'published': True,
            'created_by': 'test user',
            'modified_by': 'test user',
            'price': format(decimal.Decimal(42.42), '.2f'),
            'restrict_unique': False,
            'description': 'Optional description',
            'quantity': 5,
            'theme': fake_factory.fake_theme(event=lot_category.event).pk,
            'place': 'Some place'
        }

    def test_create(self):
        self.create()

    def test_edit(self):
        self.edit()


class SubscriptionProductServicePersistenceTest(PersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""
    application_service_class = services.SubscriptionProductService
    required_fields = (
        'subscription',
        'optional',
    )
    event = None
    lot_category = None
    lot = None

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


class SubscriptionServiceServicePersistenceTest(PersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""
    application_service_class = services.SubscriptionServiceService
    required_fields = (
        'subscription',
        'optional',
    )
    event = None
    lot_category = None
    lot = None

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


class RemoveExpiredOptionalTest(TestCase):
    """
        Testes de Mixin que processa liberação de opcional.
    """
    sub_optional_product = None
    sub_optional_service = None

    def setUp(self):
        mocker = MockFactory()

        self.sub_optional_product = mocker.fake_subscription_optional_product()
        self.sub_optional_service = mocker.fake_subscription_optional_service()

    def test_confirmed_subscription_opt_product(self):
        """
            Testa se a inscrição do opcional confirmada é ignorada.
        """
        sub = self.sub_optional_product.subscription
        sub.status = sub.CONFIRMED_STATUS

        self.sub_optional_product.subscription = sub

        removed = services.remove_expired_optional_subscription(
            self.sub_optional_product
        )

        self.assertFalse(removed)

        sub_product = models.SubscriptionProduct.objects.get(
            pk=self.sub_optional_product.pk
        )
        self.assertIsInstance(sub_product, models.SubscriptionProduct)

    def test_confirmed_subscription_opt_service(self):
        """
            Testa se a inscrição do opcional confirmada é ignorada.
        """
        sub = self.sub_optional_service.subscription
        sub.status = sub.CONFIRMED_STATUS

        self.sub_optional_service.subscription = sub

        removed = services.remove_expired_optional_subscription(
            self.sub_optional_service
        )

        self.assertFalse(removed)

        sub_service = models.SubscriptionService.objects.get(
            pk=self.sub_optional_service.pk
        )
        self.assertIsInstance(sub_service, models.SubscriptionService)

    def test_not_confirmed_subscription_opt_product_and_not_expired(self):
        """
            Testa se a inscrição do opcional é ignorada quando criada ainda
            não está confirmada, mas possui menos dias com do que configurado.
        """
        sub = self.sub_optional_product.subscription
        sub.status = sub.AWAITING_STATUS

        self.sub_optional_product.subscription = sub

        removed = services.remove_expired_optional_subscription(
            self.sub_optional_product
        )

        self.assertFalse(removed)

        sub_service = models.SubscriptionProduct.objects.get(
            pk=self.sub_optional_product.pk
        )
        self.assertIsInstance(sub_service, models.SubscriptionProduct)

    def test_not_confirmed_subscription_opt_service_and_not_expired(self):
        """
            Testa se a inscrição do opcional é ignorada quando criada ainda
            não está confirmada, mas possui menos dias com do que configurado.
        """
        sub = self.sub_optional_service.subscription
        sub.status = sub.AWAITING_STATUS

        self.sub_optional_service.subscription = sub

        removed = services.remove_expired_optional_subscription(
            self.sub_optional_service
        )

        self.assertFalse(removed)

        sub_service = models.SubscriptionService.objects.get(
            pk=self.sub_optional_service.pk
        )
        self.assertIsInstance(sub_service, models.SubscriptionService)

    def test_not_confirmed_subscription_opt_product_and_expired(self):
        """
            Testa se a inscrição do opcional é realmente removida quando criada
            com mais de dias do que configurado.
        """
        sub_optional = self.sub_optional_product

        sub = sub_optional.subscription
        sub.status = sub.AWAITING_STATUS
        sub.created = datetime.now() - timedelta(days=20)

        sub_optional.subscription = sub

        removed = services.remove_expired_optional_subscription(
            sub_optional,
            7
        )

        self.assertTrue(removed)

        with self.assertRaises(models.SubscriptionProduct.DoesNotExist):
            models.SubscriptionProduct.objects.get(
                pk=sub_optional.pk
            )

    def test_not_confirmed_subscription_opt_service_and_expired(self):
        """
            Testa se a inscrição do opcional é realmente removida quando criada
            com mais de dias do que configurado.
        """
        sub_optional = self.sub_optional_service

        sub = sub_optional.subscription
        sub.status = sub.AWAITING_STATUS
        sub.created = datetime.now() - timedelta(days=20)

        sub_optional.subscription = sub

        removed = services.remove_expired_optional_subscription(
            sub_optional,
            7
        )

        self.assertTrue(removed)

        with self.assertRaises(models.SubscriptionService.DoesNotExist):
            models.SubscriptionService.objects.get(
                pk=sub_optional.pk
            )


class SubscriptionOptionalRemoveExpiredOptionalTest(TestCase):
    """
        Testes de liberação de opcional através do processamento de inscrições
        de opcionais a partir de um número de dias configurado.
    """

    def test_release_sub_optional_product(self):
        """
            Caso nenhum 'número de dias para liberação (release_days) não
            for informado
        """
        mocker = MockFactory()
        sub_optional = mocker.fake_subscription_optional_product()

        sub = sub_optional.subscription
        sub.status = sub.AWAITING_STATUS

        service = services.SubscriptionProductService(instance=sub_optional)
        removed = service.release_optional()
        self.assertFalse(removed)

        sub.created = datetime.now() - timedelta(days=30)
        sub_optional.subscription = sub

        service = services.SubscriptionProductService(instance=sub_optional)
        removed = service.release_optional()
        self.assertTrue(removed)

    def test_release_sub_optional_service(self):
        """
            Caso nenhum 'número de dias para liberação (release_days) não
            for informado
        """
        mocker = MockFactory()
        sub_optional = mocker.fake_subscription_optional_service()

        sub = sub_optional.subscription
        sub.status = sub.AWAITING_STATUS

        sub_optional.subscription = sub

        service = services.SubscriptionServiceService(instance=sub_optional)
        removed = service.release_optional()
        self.assertFalse(removed)

        sub.created = datetime.now() - timedelta(days=30)
        sub_optional.subscription = sub

        service = services.SubscriptionServiceService(instance=sub_optional)
        removed = service.release_optional()
        self.assertTrue(removed)
