from decimal import Decimal

from django.test import TestCase

from addon.tests import MockFactory as AddonMockFactory
from gatheros_event.tests.mocks import MockFactory as EventMockFactory
from gatheros_event.constants import FREE_EVENT_FEATURES, PAID_EVENT_FEATURES
from gatheros_event.helpers.event_business import is_paid_event, is_free_event
from gatheros_subscription.tests.mocks import MockFactory


class FeatureConfigurationTest(TestCase):

    def setUp(self):
        self.event_mock_factory = EventMockFactory()
        self.addon_mock_factory = AddonMockFactory()
        self.mock_factory = MockFactory()

    def test_change_event_free_to_paid_by_lots(self):
        # Testing with a truly free event
        event = self.event_mock_factory.fake_event()
        self.assertTrue(is_free_event(event))

        # Asserting we now have a paid event
        self.mock_factory.fake_paid_lot(event=event)
        self.assertTrue(is_paid_event(event))

        # Validating that the event now has all the paid features
        for feature, value in PAID_EVENT_FEATURES.items():
            attr = getattr(event.feature_configuration, feature)
            self.assertEqual(attr, value)

    def test_change_event_free_to_paid_by_products(self):
        # Testing with a truly free event
        event = self.event_mock_factory.fake_event()
        self.assertTrue(is_free_event(event))

        # Asserting we now have a paid event
        first_lot = event.lots.first()
        lot_cat = first_lot.category = self.mock_factory.fake_lot_category(
            event)
        first_lot.save()
        price = Decimal(10)
        self.addon_mock_factory.fake_product(lot_category=lot_cat, price=price)
        self.assertTrue(is_paid_event(event))

        # Validating that the event now has all the paid features
        for feature, value in PAID_EVENT_FEATURES.items():
            attr = getattr(event.feature_configuration, feature)
            self.assertEqual(attr, value)

    def test_change_event_free_to_paid_by_services(self):
        # Testing with a truly free event
        event = self.event_mock_factory.fake_event()
        self.assertTrue(is_free_event(event))

        # Asserting we now have a paid event
        first_lot = event.lots.first()
        lot_cat = first_lot.category = self.mock_factory.fake_lot_category(
            event)
        first_lot.save()
        price = Decimal(10)
        self.addon_mock_factory.fake_service(lot_category=lot_cat, price=price)
        self.assertTrue(is_paid_event(event))

        # Validating that the event now has all the paid features
        for feature, value in PAID_EVENT_FEATURES.items():
            attr = getattr(event.feature_configuration, feature)
            self.assertEqual(attr, value)

    def test_change_event_paid_to_free_by_lots(self):
        # Testing with a truly paid event
        event = self.event_mock_factory.fake_event()
        paid_lot = self.mock_factory.fake_paid_lot(event=event)
        self.assertTrue(is_paid_event(event))

        # Asserting we now have a free event
        paid_lot.price = 0
        paid_lot.save()
        self.assertTrue(is_free_event(event))

        # Validating that the event now has all the free features
        for feature, value in FREE_EVENT_FEATURES.items():
            attr = getattr(event.feature_configuration, feature)
            self.assertEqual(attr, value)

    def test_change_event_paid_to_free_by_products(self):
        # Testing with a truly paid event
        event = self.event_mock_factory.fake_event()
        first_lot = event.lots.first()
        lot_cat = first_lot.category = self.mock_factory.fake_lot_category(
            event)
        first_lot.save()
        price = Decimal(10)
        paid_product = self.addon_mock_factory.fake_product(
            lot_category=lot_cat, price=price)

        self.assertTrue(is_paid_event(event))

        # Asserting we now have a free event
        paid_product.liquid_price = 0
        paid_product.save()
        self.assertTrue(is_free_event(event))

        # Validating that the event now has all the free features
        for feature, value in FREE_EVENT_FEATURES.items():
            attr = getattr(event.feature_configuration, feature)
            self.assertEqual(attr, value)

    def test_change_event_paid_to_free_by_services(self):
        # Testing with a truly paid event
        event = self.event_mock_factory.fake_event()
        first_lot = event.lots.first()
        lot_cat = first_lot.category = self.mock_factory.fake_lot_category(
            event)
        first_lot.save()
        price = Decimal(10)
        paid_service = self.addon_mock_factory.fake_service(
            lot_category=lot_cat, price=price)

        self.assertTrue(is_paid_event(event))

        # Asserting we now have a free event
        paid_service.liquid_price = 0
        paid_service.save()
        self.assertTrue(is_free_event(event))

        # Validating that the event now has all the free features
        for feature, value in FREE_EVENT_FEATURES.items():
            attr = getattr(event.feature_configuration, feature)
            self.assertEqual(attr, value)
