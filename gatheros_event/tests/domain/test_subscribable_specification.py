from datetime import datetime, timedelta

from test_plus.test import TestCase

from gatheros_event.event_specifications import Subscribable
from gatheros_event.tests.mocks import MockFactory as EventFactory
from gatheros_subscription.tests.mocks import MockFactory as SubFactory


class SubscribableSpecificationTest(TestCase):

    @staticmethod
    def _clean_event(event):
        event.lots.all().delete()
        return event

    def setUp(self):
        self.event_factory = EventFactory()
        self.sub_factory = SubFactory()
        self.empty_event = self._clean_event(self.event_factory.fake_event())
        self.future_event = self._clean_event(self.event_factory.fake_event())
        self.past_event = self._clean_event(self.event_factory.fake_event())
        self.present_event = self._clean_event(self.event_factory.fake_event())

        # Creating future lots
        for i in range(4):
            start = datetime.now() + timedelta(days=1)
            end = datetime.now() + timedelta(days=2)

            self.sub_factory.fake_lot(self.future_event, date_start=start,
                                      date_end=end)

        # Creating past lots
        for i in range(4):
            start = datetime.now() - timedelta(days=2)
            end = datetime.now() - timedelta(days=1)

            self.sub_factory.fake_lot(self.past_event, date_start=start,
                                      date_end=end)

        # Creating future and past lots
        for i in range(4):
            start = datetime.now() + timedelta(days=1)
            end = datetime.now() + timedelta(days=2)

            self.sub_factory.fake_lot(self.present_event, date_start=start,
                                      date_end=end)
        for i in range(4):
            start = datetime.now() - timedelta(days=2)
            end = datetime.now() - timedelta(days=1)

            self.sub_factory.fake_lot(self.present_event, date_start=start,
                                      date_end=end)

    # ======= is_specification =======

    def test_is_future_spec(self):
        root_specification = Subscribable()
        self.assertTrue(root_specification.is_satisfied_by(self.future_event))

    def test_is_past_spec(self):
        root_specification = Subscribable()
        self.assertFalse(root_specification.is_satisfied_by(self.past_event))

    def test_is_present_spec(self):
        root_specification = Subscribable()
        self.assertTrue(root_specification.is_satisfied_by(self.present_event))

    # ======= not_specification =======

    def test_not_future_spec(self):
        root_specification = Subscribable().not_specification()
        self.assertFalse(root_specification.is_satisfied_by(self.future_event))

    def test_not_past_spec(self):
        root_specification = Subscribable().not_specification()
        self.assertTrue(root_specification.is_satisfied_by(self.past_event))

    def test_not_present_spec(self):
        root_specification = Subscribable().not_specification()
        self.assertFalse(root_specification.is_satisfied_by(self.present_event))
