from datetime import datetime, timedelta

from django.db import IntegrityError
from django.test import TestCase

from gatheros_event.models import Category, Event, Organization
from gatheros_subscription.models import Lot


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
        '005_lot',
        '006_subscription',
    ]

    def _get_event( self, **kwargs ):
        event = Event.objects.get(**kwargs)
        event.date_start = datetime.now() - timedelta(days=10)
        event.date_end = datetime.now() + timedelta(days=1)
        event.save()
        return event

    def test_disabled_subscription_no_lots( self ):
        event = self._get_event(pk=5)
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

        # At least on lot created
        self.assertEqual(event.lots.count(), 1)

        event.subscription_type = Event.SUBSCRIPTION_DISABLED
        event.save()

        # When returning to disabled, all lots are deleted
        self.assertEqual(event.lots.count(), 0)

    def test_disable_subscription_with_subscriptions( self ):
        event = self._get_event(pk=1)
        # Fixture is SUBSCRIPTION_SIMPLE
        self.assertEqual(event.subscription_type, Event.SUBSCRIPTION_SIMPLE)
        self.assertEqual(event.lots.count(), 1)

        lot = event.lots.first()
        self.assertEqual(lot.subscriptions.count(), 4)

        # Not allowed to disable subscription when there are subscriptions
        with self.assertRaises(Exception):
            event.subscription_type = Event.SUBSCRIPTION_DISABLED
            event.save()

    def test_simple_subscription_one_internal_lot( self ):
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

    def test_subscription_by_lot_creates_external_lot( self ):
        event = self._get_event(pk=5)
        # Fixture is SUBSCRIPTION_DISABLED
        self.assertEqual(event.subscription_type, Event.SUBSCRIPTION_DISABLED)

        event.subscription_type = Event.SUBSCRIPTION_BY_LOTS
        event.save()
        # When converting to SUBSCRIPTION_BY_LOTS, one lot is created
        self.assertEqual(event.lots.count(), 1)

        lot = event.lots.first()
        self.assertFalse(lot.internal)

    def test_enable_simple_subscription_no_lots( self ):
        event = self._get_event(pk=5)
        # Fixture is SUBSCRIPTION_DISABLED
        self.assertEqual(event.subscription_type, Event.SUBSCRIPTION_DISABLED)

        event.subscription_type = Event.SUBSCRIPTION_SIMPLE
        event.save()
        # When configuring to SUBSCRIPTION_SIMPLE, one internal lot is created automatically
        self.assertEqual(event.lots.count(), 1)

        lot = event.lots.first()
        self.assertTrue(lot.internal)

    def test_enable_simples_subscription_lots_with_no_subscriptions( self ):
        # Fixture is SUBSCRIPTION_BY_LOTS
        event = Event.objects.get(pk=6)

        # Fixture has 4 lots related
        self.assertEqual(event.lots.count(), 4)

        # Event MUST NOT have subscription
        for lot in event.lots.all():
            lot.subscriptions.all().delete()

        event.subscription_type = Event.SUBSCRIPTION_SIMPLE
        event.save()

        # Merge lots into ONE
        self.assertEqual(event.lots.count(), 1)

    def test_enable_simples_subscription_lots_with_subscriptions( self ):
        # Fixture is SUBSCRIPTION_BY_LOTS
        event = Event.objects.get(pk=11)
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

    def test_enable_subscription_by_lots_no_lots( self ):
        event = self._get_event(pk=5)
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

    def test_enable_subscription_by_lots_with_lots( self ):
        event = Event.objects.get(pk=1)

        # Fixture is SUBSCRIPTION_SIMPLE
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
