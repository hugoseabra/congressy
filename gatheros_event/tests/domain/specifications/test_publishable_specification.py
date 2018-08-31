from test_plus.test import TestCase

from gatheros_event.event_specifications import EventPublishable
from gatheros_event.tests.mocks import MockFactory as EventFactory
from gatheros_subscription.tests.mocks import MockFactory as SubFactory


class EventPublishableSpecificationTest(TestCase):

    @staticmethod
    def _clean_event(event):
        event.lots.all().delete()
        return event

    def setUp(self):
        self.event_factory = EventFactory()

        self.event_factory = EventFactory()
        self.sub_factory = SubFactory()

        self.free_event = self.event_factory.fake_event()
        self.paid_event = self.event_factory.fake_event()
        for i in range(4):
            self.sub_factory.fake_paid_lot(event=self.paid_event)

    # ======= is_specification =======

    def test_paid_event_is_spec(self):
        root_specification = EventPublishable()
        self.assertTrue(root_specification.is_satisfied_by(self.paid_event))

    def test_free_event_is_spec(self):
        root_specification = EventPublishable()
        self.assertTrue(root_specification.is_satisfied_by(self.free_event))

    # ======= not_specification =======

    def test_paid_event_not_spec(self):
        root_specification = EventPublishable().not_specification()
        self.assertFalse(root_specification.is_satisfied_by(self.paid_event))

    def test_free_event_not_spec(self):
        root_specification = EventPublishable().not_specification()
        self.assertFalse(root_specification.is_satisfied_by(self.free_event))
