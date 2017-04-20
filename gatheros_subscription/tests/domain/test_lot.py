from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase

from gatheros_event.models import Category, Event, Organization
from gatheros_subscription.models import Lot


class LotModelTest(TestCase):
    fixtures = [
        'kanu_locations_city_test',
        '003_occupation',
        '004_category',
        '005_user',
        '006_person',
        '007_organization',
    ]

    def test_date_start_date_end_before_event_date_start(self):
        event = self._create_event()
        lot = Lot(name='Lot tests', event=event, date_start=datetime.now() + timedelta(hours=1))

        with self.assertRaises(ValidationError) as e:
            lot.save()

        self.assertTrue('date_start' in dict(e.exception).keys())

        lot.date_start = datetime.now() - timedelta(days=3)
        lot.date_end = datetime.now() + timedelta(hours=1)

        with self.assertRaises(ValidationError) as e:
            lot.save()

        self.assertTrue('date_end' in dict(e.exception).keys())

    def test_internal_when_subscription_simple(self):
        event = self._create_event(type=Event.SUBSCRIPTION_SIMPLE)
        lot = event.lots.first()
        lot.internal = False

        with self.assertRaises(ValidationError) as e:
            lot.save()

        self.assertTrue('internal' in dict(e.exception).keys())

    def test_paid_lot_with_limit(self):
        price = 55.00
        limit = 10

        event = self._create_event(type=Event.SUBSCRIPTION_BY_LOTS)
        # Lot is external
        lot = event.lots.first()
        lot.price = 55.00

        # Paid lots MUST HAVE limit
        with self.assertRaises(ValidationError) as e:
            lot.save()

        self.assertTrue('limit' in dict(e.exception).keys())

        lot.limit = limit
        lot.save()
        self.assertEqual(lot.price, price)
        self.assertEqual(lot.limit, limit)

    def test_paied_lot_must_be_external(self):
        price = 55.00

        event = self._create_event(type=Event.SUBSCRIPTION_SIMPLE)
        # Lot is internal
        lot = event.lots.first()
        lot.price = price

        # internal lots must be FREE, it means, empty price
        with self.assertRaises(ValidationError) as e:
            lot.save()

        self.assertTrue('price' in dict(e.exception).keys())

        event.subscription_type = Event.SUBSCRIPTION_BY_LOTS
        event.save()

        # Lot is internal
        lot = event.lots.first()
        lot.price = price
        lot.limit = 100
        lot.save()

        # external lots MAY BE paied
        self.assertEqual(lot.price, price)

    def test_lot_must_not_be_internal_when_subscription_by_lots(self):
        event = self._create_event(type=Event.SUBSCRIPTION_BY_LOTS)
        # Lot is external
        lot = event.lots.first()
        lot.internal = True

        # Event with SUBSCRIPTION_BY_LOTS MUST NOT have internal lots
        with self.assertRaises(ValidationError) as e:
            lot.save()

        self.assertTrue('internal' in dict(e.exception).keys())

    def _create_event(self, type=Event.SUBSCRIPTION_DISABLED):
        return Event.objects.create(
            name='Event tests',
            organization=Organization.objects.first(),
            category=Category.objects.first(),
            subscription_type=type,
            date_start=datetime.now(),
            date_end=datetime.now() + timedelta(days=1)
        )
