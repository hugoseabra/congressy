"""
    Mock factory used during tests to create required gatheros subscription
    domain objects.
"""
from datetime import datetime, timedelta

from faker import Faker

from gatheros_event.models import Event
from gatheros_subscription.models import Lot, LotCategory


class MockFactory:
    """
        Mock Factory Implementation
    """

    def __init__(self):
        self.fake_factory = Faker('pt_BR')

    def fake_lot(self, event: Event):
        if not isinstance(event, Event):
            raise Exception("'{}' is not instance of Event".format(event))

        return Lot.objects.create(
            event=event,
            name=self.fake_factory.name(),
            date_start=datetime.now() + timedelta(days=2),
            date_end=event.date_start,
        )

    def fake_paid_lot(self, event: Event, amount: int = 10):
        if not isinstance(event, Event):
            raise Exception("'{}' is not instance of Event".format(event))

        return Lot.objects.create(
            event=event,
            price=amount,
            name=self.fake_factory.name(),
            date_start=datetime.now() + timedelta(days=2),
            date_end=event.date_start,
        )

    def fake_private_lot(self, event: Event):
        if not isinstance(event, Event):
            raise Exception("'{}' is not instance of Event".format(event))

        return Lot.objects.create(
            event=event,
            name=self.fake_factory.name(),
            date_start=datetime.now() + timedelta(days=2),
            date_end=event.date_start,
            private=True,
        )

    def fake_private_paid_lot(self, event: Event, amount: int = 10):
        if not isinstance(event, Event):
            raise Exception("'{}' is not instance of Event".format(event))

        return Lot.objects.create(
            event=event,
            price=amount,
            private=True,
            name=self.fake_factory.name(),
            date_start=datetime.now() + timedelta(days=2),
            date_end=event.date_start,
        )

    def fake_lot_category(self, event: Event):
        if not isinstance(event, Event):
            raise Exception("'{}' is not instance of Event".format(event))

        return LotCategory.objects.create(
            event=event,
            name=self.fake_factory.name(),
            active=True,
        )

    @staticmethod
    def add_category_to_lot(lot: Lot, category: LotCategory):
        if not isinstance(lot, Lot):
            raise Exception("'{}' is not instance of Lot".format(lot))

        if not isinstance(category, LotCategory):
            raise Exception(
                "'{}.{}' is not instance of LotCategory".format(
                    category,
                    category.__class__,
                )
            )

        lot.category = category
        lot.save()
