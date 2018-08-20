from decimal import Decimal

from test_plus.test import TestCase

from addon.tests.mock_factory import MockFactory as AddonFactory
from gatheros_event.event_specifications import Payable
from gatheros_event.tests.mocks import MockFactory as EventFactory
from gatheros_subscription.tests.mocks import MockFactory as SubFactory


class SpecificationTest(TestCase):

    def setUp(self):
        self.event_factory = EventFactory()
        self.sub_factory = SubFactory()
        self.addon_factory = AddonFactory()

        self.free_event = self.event_factory.fake_event()

        self.paid_lot_event = self.event_factory.fake_event()
        for i in range(4):
            self.sub_factory.fake_paid_lot(event=self.paid_lot_event)

        # Products
        self.paid_product_event = self.event_factory.fake_event()
        lot = self.paid_product_event.lots.first()
        lot.category = self.sub_factory.fake_lot_category(
            self.paid_product_event)
        lot.save()

        for i in range(4):
            p = Decimal(15.99)
            self.addon_factory.fake_product(lot_category=lot.category, price=p)

        self.free_product_event = self.event_factory.fake_event()
        lot = self.free_product_event.lots.first()
        lot.category = self.sub_factory.fake_lot_category(
            self.free_product_event)
        lot.save()
        for i in range(4):
            self.addon_factory.fake_product(lot_category=lot.category)

        # Services
        self.paid_service_event = self.event_factory.fake_event()
        lot = self.paid_service_event.lots.first()
        lot.category = self.sub_factory.fake_lot_category(
            self.paid_service_event)
        lot.save()

        for i in range(4):
            p = Decimal(15.99)
            self.addon_factory.fake_service(lot_category=lot.category, price=p)

        self.free_service_event = self.event_factory.fake_event()
        lot = self.free_service_event.lots.first()
        lot.category = self.sub_factory.fake_lot_category(
            self.free_service_event)
        lot.save()
        for i in range(4):
            self.addon_factory.fake_service(lot_category=lot.category)

    # ======= is_specification =======

    def test_is_free_lots_spec(self):
        root_specification = Payable()
        self.assertFalse(root_specification.is_satisfied_by(self.free_event))

    def test_is_paid_lots_spec(self):
        root_specification = Payable()
        self.assertTrue(root_specification.is_satisfied_by(self.paid_lot_event))

    def test_is_free_products_spec(self):
        root_specification = Payable()
        self.assertFalse(
            root_specification.is_satisfied_by(self.free_product_event))

    def test_is_paid_products_spec(self):
        root_specification = Payable()
        self.assertTrue(
            root_specification.is_satisfied_by(self.paid_product_event))

    def test_is_free_services_spec(self):
        root_specification = Payable()
        self.assertFalse(
            root_specification.is_satisfied_by(self.free_service_event))

    def test_is_paid_services_spec(self):
        root_specification = Payable()
        self.assertTrue(
            root_specification.is_satisfied_by(self.paid_service_event))

    # ======= not_specification =======

    def test_is_not_free_lot_spec(self):
        root_specification = Payable().not_specification()
        self.assertTrue(root_specification.is_satisfied_by(self.free_event))

    def test_is_not_paid_lot_spec(self):
        root_specification = Payable().not_specification()
        self.assertFalse(
            root_specification.is_satisfied_by(self.paid_lot_event))

    def test_is_not_free_products_spec(self):
        root_specification = Payable().not_specification()
        self.assertTrue(
            root_specification.is_satisfied_by(self.free_product_event))

    def test_is_not_paid_products_spec(self):
        root_specification = Payable().not_specification()
        self.assertFalse(
            root_specification.is_satisfied_by(self.paid_product_event))

    def test_is_not_free_services_spec(self):
        root_specification = Payable().not_specification()
        self.assertTrue(
            root_specification.is_satisfied_by(self.free_service_event))

    def test_is_not_paid_services_spec(self):
        root_specification = Payable().not_specification()
        self.assertFalse(
            root_specification.is_satisfied_by(self.paid_service_event))
