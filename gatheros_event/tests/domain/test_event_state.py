from test_plus.test import TestCase

from gatheros_event.event_state import EventState
from gatheros_event.tests.mocks import MockFactory as EventMockFactory
from gatheros_subscription.tests.mocks import MockFactory as SubMockFactory


class EventPrivacyStateTest(TestCase):

    def setUp(self):
        self.event_factory = EventMockFactory()
        self.subscription_factory = SubMockFactory()

    def test_no_subs_public_only_valid_lots(self):
        event = self.event_factory.fake_event()

        for i in range(5):
            self.subscription_factory.fake_lot(event=event)

        state = EventState(event=event)
        self.assertTrue(state.is_public())
        self.assertFalse(state.is_private())

    def test_no_subs_public_hybrid_valid_lots(self):
        event = self.event_factory.fake_event()

        for i in range(5):
            self.subscription_factory.fake_lot(event=event)

        for i in range(5):
            self.subscription_factory.fake_paid_lot(event=event)

        state = EventState(event=event)
        self.assertTrue(state.is_public())
        self.assertFalse(state.is_private())

    def test_no_subs_private_only_valid_lots(self):
        event = self.event_factory.fake_event()

        self._make_event_private(event)

        for i in range(5):
            self.subscription_factory.fake_private_lot(event=event)

        state = EventState(event=event)
        self.assertFalse(state.is_public())
        self.assertTrue(state.is_private())

    @staticmethod
    def _make_event_private(event):

        for lot in event.lots.all():
            lot.private = True
            lot.save()
