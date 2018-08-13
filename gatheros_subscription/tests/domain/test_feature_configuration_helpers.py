from django.test import TestCase

from gatheros_event.tests.mocks import MockFactory as EventMockFactory
from addon.tests import MockFactory as AddonMockFactory
from gatheros_subscription.helpers.feature_identifier import (
    is_free_event,
)
from gatheros_subscription.tests.mocks import MockFactory


class FeatureConfigurationTest(TestCase):

    def setUp(self):
        self.event_mock_factory = EventMockFactory()
        self.addon_mock_factory = AddonMockFactory()
        self.mock_factory = MockFactory()

    def test_is_free(self):
        # Testing with a truly free event
        clean_event = self.event_mock_factory.fake_event()
        self.assertTrue(is_free_event(clean_event))

        # Testing with a paid by lote event.
        paid_lot_event = self.event_mock_factory.fake_event()
        self.mock_factory.fake_paid_lot(event=paid_lot_event)
        self.assertFalse(is_free_event(paid_lot_event))

        # Test with paid optional service
        paid_opt_service_event = self.event_mock_factory.fake_event()

        paid_opt_service_lot = self.mock_factory.fake_lot(
            paid_opt_service_event)
        paid_opt_service_lot_cat = self.mock_factory.fake_lot_category(
            paid_opt_service_event)
        self.mock_factory.add_category_to_lot(paid_opt_service_lot,
                                              paid_opt_service_lot_cat)

        self.addon_mock_factory.fake_service(
            lot_category=paid_opt_service_lot_cat,
            price=10,
        )
        self.assertFalse(is_free_event(paid_opt_service_event))

        # Test with paid optional product
        paid_opt_product_event = self.event_mock_factory.fake_event()

        paid_opt_product_lot = self.mock_factory.fake_lot(
            paid_opt_product_event)
        paid_opt_product_lot_cat = self.mock_factory.fake_lot_category(
            paid_opt_product_event)
        self.mock_factory.add_category_to_lot(paid_opt_product_lot,
                                              paid_opt_product_lot_cat)

        self.addon_mock_factory.fake_product(
            lot_category=paid_opt_product_lot_cat,
            price=10,
        )
        self.assertFalse(is_free_event(paid_opt_product_event))
