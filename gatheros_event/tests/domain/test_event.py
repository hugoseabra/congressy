from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase

from gatheros_event.models import Category, Event, Organization


class EventModelTest(TestCase):
    fixtures = [
        'kanu_locations_city_test',
        '003_occupation',
        '004_category',
        '005_user',
        '006_person',
        '007_organization',
    ]

    def test_date_start_before_date_end(self):
        event = Event(
            name='Event tests',
            organization=Organization.objects.first(),
            category=Category.objects.first(),
            subscription_type=Event.SUBSCRIPTION_DISABLED,
            date_start=datetime.now(),
            date_end=datetime.now() - timedelta(days=1)
        )

        with self.assertRaises(ValidationError) as e:
            event.save()

        self.assertTrue('date_start' in dict(e.exception).keys())

    # @TODO Testar
    def test_place_of_organization_in_event(self):
        pass

