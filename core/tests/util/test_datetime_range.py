from datetime import datetime, timedelta

from test_plus.test import TestCase

from core.util.date import DateTimeRange


class DateTimeRangeTests(TestCase):

    def test_working_example(self):
        now = datetime.now()
        later = now + timedelta(days=1)
        range_ = DateTimeRange(start=now, stop=later)

        # In middle of range
        in_range = now + timedelta(hours=1)
        self.assertTrue(in_range in range_)

        # In start of range
        in_range = now
        self.assertTrue(in_range in range_)

        # In end of range
        in_range = later
        self.assertTrue(in_range in range_)

    def test_failing_example(self):
        now = datetime.now()
        later = now + timedelta(days=1)
        range_ = DateTimeRange(start=now, stop=later)

        # In the future
        not_in_range = now + timedelta(days=2)
        self.assertFalse(not_in_range in range_)

        # In the past
        not_in_range = now - timedelta(days=2)
        self.assertFalse(not_in_range in range_)
