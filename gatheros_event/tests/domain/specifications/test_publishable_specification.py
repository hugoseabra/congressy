from test_plus.test import TestCase

from gatheros_event.event_specifications import EventPublishable
from gatheros_event.tests.mocks import MockFactory as EventFactory
from gatheros_subscription.tests.mocks import MockFactory as SubFactory


class EventPublishableSpecificationTest(TestCase):

    @staticmethod
    def _clean_event(event):
        event.lots.all().delete()
        return event

    @staticmethod
    def _set_description(event):
        event.info.description = 'aaaa'
        event.save()

    def setUp(self):
        self.event_factory = EventFactory()
        self.sub_factory = SubFactory()
        self.spec = EventPublishable()

    def test_unsubscribable_event(self):
        event = self._clean_event(self.event_factory.fake_event())
        self._set_description(event)
        self.assertFalse(self.spec.is_satisfied_by(event))
        self.sub_factory.fake_lot(event=event)
        self.assertTrue(self.spec.is_satisfied_by(event))

    def test_undescribed_event(self):
        event = self.event_factory.fake_event()
        self.sub_factory.fake_lot(event=event)
        self.assertFalse(self.spec.is_satisfied_by(event))
        self._set_description(event)
        self.assertTrue(self.spec.is_satisfied_by(event))

    def test_paid_event(self):
        event = self.event_factory.fake_event()
        self._set_description(event)
        for i in range(4):
            self.sub_factory.fake_paid_lot(event=event)
        # self.assertFalse(self.spec.is_satisfied_by(event))
        paying_org = self.event_factory.fake_paying_organization()
        event.organization = paying_org
        event.save()
        self.assertTrue(self.spec.is_satisfied_by(event))
