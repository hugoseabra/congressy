from django.conf import settings
from django.db import IntegrityError
from django.test import TestCase
from kanu_locations.models import City

from gatheros_event.models import Event, Person
from gatheros_subscription.models import Subscription


class SubscriptionModelTest(TestCase):
    fixtures = [
        'kanu_locations_city_test',
        '003_occupation',
        '004_category',
        '005_user',
        '006_person',
        '007_organization',
        '009_place',
        '010_event',
        '004_lot',
        '005_subscription',
    ]

    def test_no_subscription_limit_exceeded(self):
        event = Event.objects.get(pk=1)
        self.assertEqual(event.lots.count(), 1)

        lot = event.lots.first()

        # Sets number of subscription as limit
        lot.limit = lot.subscriptions.count()
        lot.save()

        # Limit exceeded
        with self.assertRaises(IntegrityError):
            self._create_subscription(lot, None, True)

    def test_subscription_code_generated(self):
        event = Event.objects.get(pk=1)
        self.assertEqual(event.lots.count(), 1)

        lot = event.lots.last()

        # The only Person in fixture who has no subscription
        subscription = Subscription.objects.create(
            person=Person.objects.get(pk='5d20a3cd-bfac-46fb-a771-a9bfd3819bf2'),
            lot=lot,
            origin=Subscription.DEVICE_ORIGIN_WEB,
            created_by=1
        )

        self.assertEqual(len(subscription.code), 8)

    def test_subscription_number_generated(self):
        event = Event.objects.get(pk=1)
        self.assertEqual(event.lots.count(), 1)

        lot = event.lots.last()
        num_subscriptions = lot.subscriptions.count()

        # The only Person in fixture who has no subscription
        subscription = self._create_subscription(lot, None, True)

        self.assertEqual(subscription.count, num_subscriptions + 1)

    def test_confirmed_subscription_with_confirmation_date(self):
        event = Event.objects.get(pk=1)
        self.assertEqual(event.lots.count(), 1)

        # Grabs subscription
        subscription = event.lots.first().subscriptions.first()

        # By default, not attended and no attended date
        self.assertFalse(subscription.attended)
        self.assertIsNone(subscription.attended_on)

        subscription.attended = True
        subscription.save()

        # Confirmation of attendance and attendance date
        self.assertTrue(subscription.attended)
        self.assertIsNotNone(subscription.attended_on)

        subscription.attended = False
        subscription.save()

        # Back to default
        self.assertFalse(subscription.attended)
        self.assertIsNone(subscription.attended_on)

    def _create_person(self, persist=True):
        person = Person(
            name="Test",
            genre="M",
            city=City.objects.get(pk=5413),
            cpf="82247263631"
        )

        if persist:
            person.save()

        return person

    def _create_subscription(self, lot, person=None, persist=True):
        if person is None:
            person = self._create_person()

        subscription = Subscription(
            person=person,
            lot=lot,
            origin=Subscription.DEVICE_ORIGIN_WEB,
            created_by=1
        )

        if persist:
            person.save()
            subscription.save()

        return subscription
