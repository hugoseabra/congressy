from datetime import datetime, timedelta

from django.test import TestCase

from gatheros_event.tests.mocks import MockFactory as EventMockFactory
from gatheros_subscription.helpers.feature_identifier import (
    is_free_event,
    is_paid_event,
)
from gatheros_subscription.models import Lot


class FeatureConfigurationTest(TestCase):

    def setUp(self):
        self.fake_factory = EventMockFactory()

    def test_is_free(self):
        event = self.fake_factory.fake_event()
        self.assertTrue(is_free_event(event))

    def test_is_paid(self):
        event = self.fake_factory.fake_event()
        Lot.objects.create(
            event=event,
            name=self.fake_factory.fake_factory.name(),
            date_start=datetime.now() + timedelta(days=1),
            price=1,
        )

        self.assertTrue(is_paid_event(event))
