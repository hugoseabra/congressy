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
        '009_place',
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

    def test_place_of_organization_in_event(self):
        event = Event.objects.create(
            name='Event tests',
            organization=Organization.objects.first(),
            category=Category.objects.first(),
            subscription_type=Event.SUBSCRIPTION_DISABLED,
            date_start=datetime.now(),
            date_end=datetime.now() + timedelta(days=5)
        )

        # Grabs a different organization
        organization = Organization.objects.last()

        # Adds a place which does not belong to its organization
        event.place = organization.places.first()

        with self.assertRaises(ValidationError) as e:
            event.save()

        self.assertTrue('place' in dict(e.exception).keys())
