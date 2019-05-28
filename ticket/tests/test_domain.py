from datetime import datetime, timedelta

from django.test import TestCase
from faker import Faker

from gatheros_subscription.models import Subscription
from ticket.managers import TicketManager, LotManager
from ticket.tests import MockFactory


class TicketDomainTest(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.mock_factory = MockFactory()
        self.event = self.mock_factory.fake_event()

    def test_free_installments_limit(self):
        d = {
            'name': 'random name',
            'event': self.event.pk,
            'free_installments': 11,
        }

        self.assertFalse(TicketManager(data=d).is_valid())

        d['free_installments'] = 10

        self.assertTrue(TicketManager(data=d).is_valid())

    def test_changing_event(self):
        instance = self.mock_factory.fake_ticket(event=self.event)

        new_event = self.mock_factory.fake_event()

        d = {
            'name': 'random name',
            'event': new_event.pk,
        }

        self.assertFalse(TicketManager(data=d, instance=instance).is_valid())

        d['event'] = self.event.pk

        m = TicketManager(data=d, instance=instance)
        m.is_valid()

        self.assertTrue(TicketManager(data=d, instance=instance).is_valid())


class LotDomainTest(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.mock_factory = MockFactory()
        self.fake_factory = Faker('pt_BR')
        self.event = self.mock_factory.fake_event()

    def test_date_conflicts(self):
        t = self.mock_factory.fake_ticket(event=self.event)

        n = datetime.now()

        d = {
            'ticket': t.pk,
            'name': self.fake_factory.word(ext_word_list=None),
            'date_start': n,
            'date_end': n,
        }

        # Same date_start and date_end
        self.assertFalse(LotManager(data=d).is_valid())

        d['date_end'] = n + timedelta(days=1)

        # Different date_start and date_end, no conflicts
        self.assertTrue(LotManager(data=d).is_valid())

        # Default lot time frame is:
        # start: now
        # end: now + timedelta(days=1)
        self.mock_factory.fake_lot(ticket=t)

        # Conflict
        self.assertFalse(LotManager(data=d).is_valid())

        d['date_start'] = n + timedelta(hours=6)

        # Still Conflict
        self.assertFalse(LotManager(data=d).is_valid())

        d['date_start'] = n + timedelta(days=2)
        d['date_end'] = n + timedelta(days=3)

        # No Conflict
        self.assertTrue(LotManager(data=d).is_valid())

    def test_limit_check(self):
        t = self.mock_factory.fake_ticket(event=self.event)
        t.limit = 300
        t.save()

        d = {
            'ticket': t.pk,
            'name': self.fake_factory.word(ext_word_list=None),
            'date_start': datetime.now(),
            'date_end': datetime.now() + timedelta(days=1),
            'limit': 300,
        }

        self.assertTrue(LotManager(data=d).is_valid())

        d['limit'] = 301

        self.assertFalse(LotManager(data=d).is_valid())

    def test_price_change(self):
        t = self.mock_factory.fake_ticket(event=self.event)
        lot = self.mock_factory.fake_lot(ticket=t)

        d = {
            'ticket': lot.ticket.pk,
            'date_start': lot.date_start,
            'date_end': lot.date_end,
            'price': 300.00,
        }

        self.assertTrue(LotManager(instance=lot, data=d).is_valid())

        sub = self.mock_factory.fake_subscription(lot=lot)
        sub.status = Subscription.CONFIRMED_STATUS
        sub.save()

        self.assertFalse(LotManager(instance=lot, data=d).is_valid())

    def test_ticket_change(self):
        t = self.mock_factory.fake_ticket(event=self.event)
        lot = self.mock_factory.fake_lot(ticket=t)

        new_ticket = self.mock_factory.fake_ticket(event=self.event)

        d = {
            'ticket': new_ticket.pk,
            'date_start': lot.date_start,
            'date_end': lot.date_end,
            'price': 300.00,
        }

        self.assertFalse(LotManager(instance=lot, data=d).is_valid())

        d['ticket'] = lot.ticket.pk

        self.assertTrue(LotManager(instance=lot, data=d).is_valid())
