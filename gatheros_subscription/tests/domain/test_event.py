from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from gatheros_event.models import Category, Event, Organization, Person
from gatheros_subscription.models import Lot, Subscription


class EventModelTest(TestCase):
    fixtures = [
        'kanu_locations_city_test',
        '003_occupation',
        '004_category',
        '005_user',
        '006_person',
        '007_organization',
        '009_place',
        '010_event',
        'tests/004_lot_test',
        'tests/005_subscription_test',
    ]

    def test_disabled_subscription_no_lots(self):
        event = Event.objects.get(pk=1)
        # Fixture is SUBSCRIPTION_DISABLED
        self.assertEqual(event.subscription_type, Event.SUBSCRIPTION_DISABLED)

        event.subscription_type = Event.SUBSCRIPTION_SIMPLE
        event.save()
        # When configuring to SUBSCRIPTION_SIMPLE, one internal lot is created automatically
        self.assertEqual(event.lots.count(), 1)

        event.subscription_type = Event.SUBSCRIPTION_DISABLED
        event.save()
        # When returning to disabled, internal lot previously created is deleted
        self.assertEqual(event.lots.count(), 0)

        event.subscription_type = Event.SUBSCRIPTION_BY_LOTS
        event.save()
        # When converting to SUBSCRIPTION_BY_LOTS, one lot is created
        # adding more 2 lots
        Lot.objects.create(name='Lot tests 2', event=event, date_start=datetime.now())
        Lot.objects.create(name='Lot tests 3', event=event, date_start=datetime.now())
        # Subscription by lots accepts many lots.
        self.assertEqual(event.lots.count(), 3)

        event.subscription_type = Event.SUBSCRIPTION_DISABLED
        event.save()
        # When returning to disabled, all lots are deleted
        self.assertEqual(event.lots.count(), 0)

    def test_disable_subscription_with_subscriptions(self):
        event = Event.objects.get(pk=2)
        # Fixture is SUBSCRIPTION_SIMPLE
        self.assertEqual(event.subscription_type, Event.SUBSCRIPTION_SIMPLE)

        # Adds a subscription in lot
        lot = event.lots.first()

        # The only Person in fixture who has no subscription
        Subscription.objects.create(
            person=Person.objects.get(pk='5d20a3cd-bfac-46fb-a771-a9bfd3819bf2'),
            lot=lot,
            origin=Subscription.DEVICE_ORIGIN_WEB,
            created_by=1
        )

        with self.assertRaises(Exception):
            event.subscription_type = Event.SUBSCRIPTION_DISABLED
            event.save()

    def test_simple_subscription_one_internal_lot(self):
        """
        1. Inscrições simples não podem ter mais de um lote
        2. O único lote deve ser interno
        3. Não deve aceitar a inserção de outros lotes
        """
        event = Event.objects.create(
            name='Event tests',
            organization=Organization.objects.first(),
            category=Category.objects.first(),
            subscription_type=Event.SUBSCRIPTION_SIMPLE,
            date_start=datetime.now(),
            date_end=datetime.now() + timedelta(days=10)
        )
        self.assertEqual(event.lots.count(), 1)

        lot = event.lots.first()
        self.assertTrue(lot.internal)

        with self.assertRaises(IntegrityError):
            Lot.objects.create(
                name='Lot tests',
                event=event,
                date_start=datetime.now() - timedelta(days=5),
                internal=True
            )

    def test_subscription_by_lot_creates_external_lot(self):
        event = Event.objects.get(pk=1)
        # Fixture is SUBSCRIPTION_DISABLED
        self.assertEqual(event.subscription_type, Event.SUBSCRIPTION_DISABLED)

        event.subscription_type = Event.SUBSCRIPTION_BY_LOTS
        event.save()
        # When converting to SUBSCRIPTION_BY_LOTS, one lot is created
        self.assertTrue(event.lots.count() == 1)

        lot = event.lots.first()
        self.assertFalse(lot.internal)

    def test_enable_simple_subscription_no_lots(self):
        event = Event.objects.get(pk=1)
        # Fixture is SUBSCRIPTION_DISABLED
        self.assertEqual(event.subscription_type, Event.SUBSCRIPTION_DISABLED)

        event.subscription_type = Event.SUBSCRIPTION_SIMPLE
        event.save()
        # When configuring to SUBSCRIPTION_SIMPLE, one internal lot is created automatically
        self.assertEqual(event.lots.count(), 1)

        lot = event.lots.first()
        self.assertTrue(lot.internal)

    def test_enable_simples_subscription_lots_with_no_subscriptions(self):
        # Fixture is SUBSCRIPTION_BY_LOTS
        event = Event.objects.get(pk=4)
        # Fixture has 3 lot related
        self.assertEqual(event.lots.count(), 2)

        # Event MUST NOT have subscription
        has_subscription = False
        for lot in event.lots.all():
            if lot.subscriptions.count() > 0:
                has_subscription = True

        self.assertFalse(has_subscription)

        event.subscription_type = Event.SUBSCRIPTION_SIMPLE
        event.save()
        # Merge lots into ONE
        self.assertEqual(event.lots.count(), 1)

    def test_enable_simples_subscription_lots_with_subscriptions(self):
        # Fixture is SUBSCRIPTION_BY_LOTS
        event = Event.objects.get(pk=5)
        # Fixture has 2 lot related
        self.assertEqual(event.lots.count(), 2)

        # Event MUST have subscription in some lot
        has_subscription = False
        subscription_counter = 0
        for lot in event.lots.all():
            num_sub = lot.subscriptions.count()
            if num_sub == 0:
                continue
            has_subscription = True
            subscription_counter += lot.subscriptions.count()

        self.assertTrue(has_subscription)

        event.subscription_type = Event.SUBSCRIPTION_SIMPLE
        event.save()
        # Merge lots into ONE
        self.assertEqual(event.lots.count(), 1)

        # Subscriptions transferred to MERGED LOT
        lot = event.lots.first()
        self.assertEqual(lot.subscriptions.count(), subscription_counter)

    def test_enable_subscription_by_lots_no_lots(self):
        event = Event.objects.get(pk=1)
        # Fixture is SUBSCRIPTION_DISABLED
        self.assertEqual(event.subscription_type, Event.SUBSCRIPTION_DISABLED)

        # Event MUST NOT have LOTS
        self.assertEqual(event.lots.count(), 0)

        event.subscription_type = Event.SUBSCRIPTION_BY_LOTS
        event.save()
        # When configuring to SUBSCRIPTION_SUBSCRIPTION_BY_LOTS, one external lot is created automatically
        self.assertEqual(event.lots.count(), 1)

        # Lot must be external
        lot = event.lots.first()
        self.assertFalse(lot.internal)

    def test_enable_subscription_by_lots_with_lots(self):
        event = Event.objects.get(pk=2)
        # Fixture is SUBSCRIPTION_DISABLED
        self.assertEqual(event.subscription_type, Event.SUBSCRIPTION_SIMPLE)

        # Event MUST have ONE LOT
        self.assertEqual(event.lots.count(), 1)
        # lot MUST be internal
        lot = event.lots.first()
        self.assertTrue(lot.internal)

        event.subscription_type = Event.SUBSCRIPTION_BY_LOTS
        event.save()
        # When configuring to SUBSCRIPTION_SUBSCRIPTION_BY_LOTS, lot is converted to external
        # Event MUST have ONE LOT
        self.assertEqual(event.lots.count(), 1)
        # lot MUST be external
        lot = event.lots.first()
        self.assertFalse(lot.internal)
