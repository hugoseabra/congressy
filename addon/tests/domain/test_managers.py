""" Testes de managers do módulo de opcionais. """

import decimal
from datetime import datetime, timedelta

from test_plus.test import TestCase

from addon import models as addon_models, managers
from addon.tests.mock_factory import MockFactory
from base.tests.test_suites import ManagerPersistenceTestCase


class ThemeManagerPersistenceTest(ManagerPersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""
    manager_class = managers.ThemeManager
    required_fields = ('name', 'event')
    data_edit_to = {
        'name': 'another name edited',
    }

    def setUp(self):
        fake_factory = MockFactory()
        self.data = {
            'event': fake_factory.fake_event().pk,
            'name': 'my name',
        }

    def _create_manager(self, instance=None, data=None):

        if not data:
            data = self.data

        if 'event' not in data:
            data['event'] = MockFactory().fake_event().pk

        if instance is not None:
            manager = self.manager_class(instance=instance, data=data)
        else:
            manager = self.manager_class(data=data)

        return manager

    def test_create(self):
        self.create()

    def test_edit(self):
        self.edit()


class OptionalProductTypePersistenceTest(ManagerPersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""
    manager_class = managers.OptionalProductTypeManager
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


class OptionalServiceTypePersistenceTest(ManagerPersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""
    manager_class = managers.OptionalServiceTypeManager
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

    manager_class = managers.ProductManager
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

    def _create_manager(self, instance=None, data=None):

        static_fake_factory = MockFactory()

        if not data:
            data = self.data

        if 'optional_type' not in data:
            data[
                'optional_type'] = \
                static_fake_factory.fake_optional_product_type().pk

        if 'lot_category' not in data:
            data['lot_category'] = static_fake_factory.fake_lot_category().pk

        if instance is not None:
            manager = self.manager_class(instance=instance, data=data)
        else:
            manager = self.manager_class(data=data)

        return manager

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


class ServiceManagerPersistenceTest(ManagerPersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""

    manager_class = managers.ServiceManager
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

    def _create_manager(self, instance=None, data=None):

        static_fake_factory = MockFactory()

        if not data:
            data = self.data

        if 'optional_type' not in data:
            data[
                'optional_type'] = \
                static_fake_factory.fake_optional_service_type().pk

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
        schedule_start = datetime.now() - timedelta(days=3)
        schedule_end = datetime.now() + timedelta(days=3)
        self.data = {
            'optional_type': fake_factory.fake_optional_service_type().pk,
            'lot_category': fake_factory.fake_lot_category().pk,
            'name': 'optional name',
            'schedule_start': schedule_start.strftime('%d/%m/%Y %H:%M'),
            'schedule_end': schedule_end.strftime('%d/%m/%Y %H:%M'),
            'date_end_sub': schedule_end.strftime('%d/%m/%Y %H:%M'),
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

    manager_class = managers.SubscriptionProductManager
    required_fields = (
        'subscription',
        'optional',
    )
    fake_factory = None

    def _create_manager(self, instance=None, data=None):

        static_fake_factory = MockFactory()

        if not data:
            data = self.data

        if 'subscription' not in data:
            data['subscription'] = static_fake_factory.fake_subscription().pk

        if 'optional' not in data:
            data['optional'] = static_fake_factory.fake_product().pk

        if instance is not None:
            manager = self.manager_class(instance=instance, data=data)
        else:
            manager = self.manager_class(data=data)

        return manager

    def setUp(self):
        self.fake_factory = MockFactory()
        subscription = self.fake_factory.fake_subscription()
        lot_category = subscription.lot.category

        optional = self.fake_factory.fake_product(lot_category=lot_category)

        self.data = {
            'optional': optional.pk,
            'subscription': subscription.pk,
        }

    def test_create(self):
        self.create()

    def test_edit(self):
        self.edit()


class SubscriptionProductManagerRulesTest(TestCase):
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

        product = self.fake_factory.fake_product(lot_category=lot_category)
        product.quantity = 1
        product.save()

        product_manager = managers.SubscriptionProductManager(
            data={
                'subscription': subscription.pk,
                'optional': product.pk,
            }
        )

        self.assertTrue(product_manager.is_valid())
        product_manager.save()
        self.assertEqual(
            addon_models.SubscriptionProduct.objects.all().count(), 1)

        failing_product_manager = managers.SubscriptionProductManager(
            data={
                'subscription': failing_subscription.pk,
                'optional': product.pk,
            }
        )

        self.assertFalse(failing_product_manager.is_valid())
        self.assertIn(
            'Quantidade de inscrições já foi atingida, novas inscrições não'
            ' poderão ser realizadas',
            failing_product_manager.errors['__all__']
        )

    def test_date_end_validation_in_the_past(self):
        subscription = self.fake_factory.fake_subscription()

        past_product = self.fake_factory.fake_product(
            lot_category=subscription.lot.category)
        past_product.date_end_sub = datetime.now() - timedelta(days=1)
        past_product.save()

        product_manager = managers.SubscriptionProductManager(
            data={
                'subscription': subscription.pk,
                'optional': past_product.pk,
            }
        )
        self.assertFalse(product_manager.is_valid())
        self.assertEqual(product_manager.errors['__all__'][0],
                      'Este opcional já expirou e não aceita mais inscrições.')
        
    def test_date_end_validation_in_the_future(self):
        subscription = self.fake_factory.fake_subscription()

        future_product = self.fake_factory.fake_product(
            lot_category=subscription.lot.category)
        future_product.date_end_sub = datetime.now() + timedelta(days=1)
        future_product.save()

        product_manager = managers.SubscriptionProductManager(
            data={
                'subscription': subscription.pk,
                'optional': future_product.pk,
            }
        )
        self.assertTrue(product_manager.is_valid())
        self.assertIsInstance(product_manager.save(),
                              addon_models.SubscriptionProduct)


class SubscriptionServiceManagerPersistenceTest(ManagerPersistenceTestCase):
    """ Testes de persistência de dados: criação e edição."""

    manager_class = managers.SubscriptionServiceManager
    required_fields = (
        'subscription',
        'optional',
    )

    fake_factory = None

    def _create_manager(self, instance=None, data=None):

        static_fake_factory = MockFactory()

        if not data:
            data = self.data

        if 'subscription' not in data:
            data['subscription'] = static_fake_factory.fake_subscription().pk

        if 'optional' not in data:
            data['optional'] = static_fake_factory.fake_product().pk

        if instance is not None:
            manager = self.manager_class(instance=instance, data=data)
        else:
            manager = self.manager_class(data=data)

        return manager

    def setUp(self):
        self.fake_factory = MockFactory()

        subscription = self.fake_factory.fake_subscription()
        lot_category = subscription.lot.category

        optional = self.fake_factory.fake_service(lot_category=lot_category)

        self.data = {
            'optional': optional.pk,
            'subscription': subscription.pk,
        }

    def test_create(self):
        self.create()

    def test_edit(self):
        self.edit()


class SubscriptionServiceManagerRulesTest(TestCase):
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

        optional_service = self.fake_factory.fake_service(
            lot_category=lot_category,
        )
        optional_service.quantity = 1
        optional_service.save()

        service_manager = managers.SubscriptionServiceManager(
            data={
                'subscription': subscription.pk,
                'optional': optional_service.pk,
            }
        )

        self.assertTrue(service_manager.is_valid())
        service_manager.save()
        self.assertEqual(
            addon_models.SubscriptionService.objects.all().count(),
            1
        )

        failing_product_manager = managers.SubscriptionServiceManager(
            data={
                'subscription': failing_subscription.pk,
                'optional': optional_service.pk,
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

        # Crie dois Services
        service_1 = self.fake_factory.fake_service(
            lot_category=subscription.lot.category
        )
        service_2 = self.fake_factory.fake_service(
            lot_category=subscription.lot.category
        )

        # Configurando os dois serviços para usar a flag de sessão
        service_1.schedule_start = datetime.now()
        service_1.schedule_end = datetime.now() + timedelta(days=1)
        service_1.restrict_unique = True
        service_1.save()

        service_2.schedule_start = datetime.now()
        service_2.schedule_end = datetime.now() + timedelta(days=1)
        service_2.restrict_unique = True
        service_2.save()

        # Criando os gerenciadores de serviços
        service_1_manager = managers.SubscriptionServiceManager(
            data={
                'subscription': subscription.pk,
                'optional': service_1.pk,
            }
        )

        service_2_manager = managers.SubscriptionServiceManager(
            data={
                'subscription': subscription.pk,
                'optional': service_2.pk,
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

        # Crie dois Services
        service_1 = self.fake_factory.fake_service(
            lot_category=subscription.lot.category)
        service_2 = self.fake_factory.fake_service(
            lot_category=subscription.lot.category)

        # Configurando os dois serviços para usar a flag de sessão
        service_1.schedule_start = datetime.now()
        service_1.schedule_end = datetime.now() + timedelta(days=1)
        service_1.restrict_unique = False
        service_1.save()

        service_2.schedule_start = datetime.now()
        service_2.schedule_end = datetime.now() + timedelta(days=1)
        service_2.restrict_unique = False
        service_2.save()

        # Criando os gerenciadores de serviços
        service_1_manager = managers.SubscriptionServiceManager(
            data={
                'subscription': subscription.pk,
                'optional': service_1.pk,
            }
        )

        service_2_manager = managers.SubscriptionServiceManager(
            data={
                'subscription': subscription.pk,
                'optional': service_2.pk,
            }
        )

        # Validações
        self.assertTrue(service_1_manager.is_valid())
        service_1_manager.save()
        self.assertTrue(service_2_manager.is_valid())
        service_2_manager.save()

    def test_validation_by_session_with_flag_on_bilaterally(self):
        """Teste para verificar se a rega consegue ser aplicada de maneira
        bilateral"""

        subscription = self.fake_factory.fake_subscription()

        # Crie dois Services
        service_1 = self.fake_factory.fake_service(
            lot_category=subscription.lot.category)
        service_2 = self.fake_factory.fake_service(
            lot_category=subscription.lot.category)

        # Configurando os dois serviços para usar a flag de sessão
        service_1.schedule_start = datetime.now()
        service_1.schedule_end = datetime.now() + timedelta(days=1)
        service_1.restrict_unique = False
        service_1.save()

        service_2.schedule_start = datetime.now()
        service_2.schedule_end = datetime.now() + timedelta(days=1)
        service_2.restrict_unique = True
        service_2.save()

        # Criando os gerenciadores de serviços
        service_1_manager = managers.SubscriptionServiceManager(
            data={
                'subscription': subscription.pk,
                'optional': service_1.pk,
            }
        )

        service_2_manager = managers.SubscriptionServiceManager(
            data={
                'subscription': subscription.pk,
                'optional': service_2.pk,
            }
        )

        # Validações
        self.assertTrue(service_1_manager.is_valid())
        service_1_manager.save()
        self.assertFalse(service_2_manager.is_valid())

    def test_validation_by_theme_with_limit(self):
        # Crie uma única Subscription para ser usada para criar o
        # SubscriptionOptionalService
        subscription = self.fake_factory.fake_subscription()

        # Criando um tema e configurando seu limite para uma unica inscrição
        theme = self.fake_factory.fake_theme()
        theme.limit = 1
        theme.save()

        # Crie OptionalServices com tema.
        service = self.fake_factory.fake_service(
            lot_category=subscription.lot.category, theme=theme)

        # Criando os gerenciadores de serviços
        service_manager_1 = managers.SubscriptionServiceManager(
            data={
                'subscription': subscription.pk,
                'optional': service.pk,
            }
        )

        service_manager_2 = managers.SubscriptionServiceManager(
            data={
                'subscription': subscription.pk,
                'optional': service.pk,
            }
        )

        self.assertTrue(service_manager_1.is_valid())
        service_manager_1.save()
        self.assertFalse(service_manager_2.is_valid())

    def test_validation_by_theme_without_limit(self):
        # Crie uma única Subscription para ser usada para criar o
        # SubscriptionOptionalService
        subscription = self.fake_factory.fake_subscription()

        # Criando um tema e configurando seu limite como infinito
        theme = self.fake_factory.fake_theme()
        theme.limit = None
        theme.save()

        # Crie OptionalServices com tema.
        service = self.fake_factory.fake_service(
            lot_category=subscription.lot.category, theme=theme)

        # Criando os gerenciadores de serviços
        service_manager_1 = managers.SubscriptionServiceManager(
            data={
                'subscription': subscription.pk,
                'optional': service.pk,
            }
        )

        service_manager_2 = managers.SubscriptionServiceManager(
            data={
                'subscription': subscription.pk,
                'optional': service.pk,
            }
        )

        self.assertTrue(service_manager_1.is_valid())
        service_manager_1.save()
        self.assertTrue(service_manager_2.is_valid())
        service_manager_2.save()

    def test_date_end_validation_in_the_past(self):
        subscription = self.fake_factory.fake_subscription()

        future_service = self.fake_factory.fake_service(
            lot_category=subscription.lot.category)
        future_service.date_end_sub = datetime.now() - timedelta(days=1)
        future_service.save()

        service_manager = managers.SubscriptionServiceManager(
            data={
                'subscription': subscription.pk,
                'optional': future_service.pk,
            }
        )

        self.assertFalse(service_manager.is_valid())
        self.assertEqual(service_manager.errors['__all__'][0],
                         'Este opcional já expirou e não aceita mais '
                         'inscrições.')

    def test_date_end_validation_in_the_future(self):
        subscription = self.fake_factory.fake_subscription()

        future_service = self.fake_factory.fake_service(
            lot_category=subscription.lot.category)
        future_service.date_end_sub = datetime.now() + timedelta(days=1)
        future_service.save()

        service_manager = managers.SubscriptionServiceManager(
            data={
                'subscription': subscription.pk,
                'optional': future_service.pk,
            }
        )

        self.assertTrue(service_manager.is_valid())
        self.assertIsInstance(service_manager.save(),
                              addon_models.SubscriptionService)
