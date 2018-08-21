from test_plus.test import TestCase

from gatheros_event.event_specifications import HasSubscriptions
from gatheros_event.tests.mocks import MockFactory as EventFactory
from gatheros_subscription.tests.mocks import MockFactory as SubFactory


class HasSubscriptionsSpecificationTest(TestCase):

    @staticmethod
    def _clean_event(event):
        event.lots.all().delete()
        return event

    def setUp(self):
        self.event_factory = EventFactory()
        self.sub_factory = SubFactory()
        self.empty_event = self.event_factory.fake_event()
        self.valid_subs_event = self.event_factory.fake_event()
        self.invalid_subs_event = self.event_factory.fake_event()

        # Creating valid subscriptions
        for i in range(4):
            person = self.event_factory.fake_person()
            lot = self.valid_subs_event.lots.first()
            self.sub_factory.fake_subscription(lot, person)

        # Creating invalid subscriptions
        for i in range(4):
            person = self.event_factory.fake_person()
            lot = self.valid_subs_event.lots.first()
            self.sub_factory.fake_test_subscription(lot, person)
        for i in range(4):
            person = self.event_factory.fake_person()
            lot = self.valid_subs_event.lots.first()
            self.sub_factory.fake_unconfirmed_subscription(lot, person)

            # ======= is_specification =======

    # ======= is_specification =======

    def test_is_empty_event_spec(self):
        root_specification = HasSubscriptions()
        self.assertFalse(
            root_specification.is_satisfied_by(self.empty_event))

    def test_is_valid_subs_event_spec(self):
        root_specification = HasSubscriptions()
        self.assertTrue(
            root_specification.is_satisfied_by(self.valid_subs_event))

    def test_is_invalid_subs_event_spec(self):
        root_specification = HasSubscriptions()
        self.assertFalse(
            root_specification.is_satisfied_by(self.invalid_subs_event))

    # ======= not_specification =======

    def test_not_empty_event_spec(self):
        root_specification = HasSubscriptions().not_specification()
        self.assertTrue(
            root_specification.is_satisfied_by(self.empty_event))

    def test_not_valid_subs_event_spec(self):
        root_specification = HasSubscriptions().not_specification()
        self.assertFalse(
            root_specification.is_satisfied_by(self.valid_subs_event))

    def test_not_invalid_subs_event_spec(self):
        root_specification = HasSubscriptions().not_specification()
        self.assertTrue(
            root_specification.is_satisfied_by(self.invalid_subs_event))
