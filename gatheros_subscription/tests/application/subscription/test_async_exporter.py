from django.test import TestCase

from gatheros_subscription.helpers.async_exporter import (
    has_export_lock,
    create_export_lock,
    remove_export_lock,
)
from gatheros_subscription.tests.mocks import MockFactory


class AsyncExporterTestCase(TestCase):

    def setUp(self) -> None:
        self.mock_factory = MockFactory()
        self.event_instance = self.mock_factory.fake_event()

    def test_file_locker(self):
        self.assertFalse(has_export_lock(self.event_instance))
        create_export_lock(self.event_instance)
        self.assertTrue(has_export_lock(self.event_instance))
        remove_export_lock(self.event_instance)
        self.assertFalse(has_export_lock(self.event_instance))
