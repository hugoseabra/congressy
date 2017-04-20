from django.db import IntegrityError
from django.test import TestCase

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
    ]

    def test_no_subscription_limit_exceeded(self):
        event = Event.objects.get(pk=5)

        self.assertEqual(event.lots.count(), 2)

        # First lot MUST HAVE 2 subscriptions
        lot = event.lots.first()
        self.assertEqual(lot.subscriptions.count(), 2)

        # Lot limit MUST BE 2
        self.assertEqual(lot.limit, 2)

        # Limit exceeded
        with self.assertRaises(IntegrityError):
            # The only Person in fixture who has no subscription
            Subscription.objects.create(
                person=Person.objects.get(pk='5d20a3cd-bfac-46fb-a771-a9bfd3819bf2'),
                lot=lot,
                origin=Subscription.DEVICE_ORIGIN_WEB,
                created_by=1
            )

    def test_subscription_code_generated(self):
        event = Event.objects.get(pk=5)
        self.assertEqual(event.lots.count(), 2)

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
        event = Event.objects.get(pk=5)
        self.assertEqual(event.lots.count(), 2)

        lot = event.lots.last()
        num_subscriptions = lot.subscriptions.count()

        # The only Person in fixture who has no subscription
        subscription = Subscription.objects.create(
            person=Person.objects.get(pk='5d20a3cd-bfac-46fb-a771-a9bfd3819bf2'),
            lot=lot,
            origin=Subscription.DEVICE_ORIGIN_WEB,
            created_by=1
        )

        self.assertEqual(subscription.count, num_subscriptions + 1)

    def test_confirmed_subscription_with_confirmation_date(self):
        event = Event.objects.get(pk=5)
        self.assertEqual(event.lots.count(), 2)

        # The only Person in fixture who has no subscription
        subscription = Subscription.objects.create(
            person=Person.objects.get(pk='5d20a3cd-bfac-46fb-a771-a9bfd3819bf2'),
            lot=event.lots.last(),
            origin=Subscription.DEVICE_ORIGIN_WEB,
            created_by=1
        )
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
