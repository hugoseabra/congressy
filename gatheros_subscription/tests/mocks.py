"""
    Mock factory used during tests to create required gatheros subscription
    domain objects.
"""
from datetime import datetime, timedelta

from faker import Faker

from gatheros_event.models import Event, Person, Organization, Category
from gatheros_subscription.models import Lot, LotCategory, Subscription


class MockFactory:
    """
        Mock Factory Implementation
    """

    def __init__(self):
        self.fake_factory = Faker('pt_BR')

    def fake_person(self):
        return Person.objects.create(name=self.fake_factory.name())

    def fake_organization(self):
        return Organization.objects.create(
            name=self.fake_factory.company(),
            email=self.fake_factory.email(),
        )

    def fake_event(self, organization=None):

        if not organization:
            organization = self.fake_organization()

        return Event.objects.create(
            organization=organization,
            name='Event: ' + ' '.join(self.fake_factory.words(nb=3)),
            date_start=datetime.now() + timedelta(days=3),
            date_end=datetime.now() + timedelta(days=4),
            category=Category.objects.first(),
        )

    def fake_lot(self, event: Event, date_start=None, date_end=None):
        if not isinstance(event, Event):
            raise Exception("'{}' is not instance of Event".format(event))

        if date_start is None:
            date_start = datetime.now()

        if date_end is None:
            date_end = event.date_end

        return Lot.objects.create(
            event=event,
            name=self.fake_factory.name(),
            active=True,
            date_start=date_start,
            date_end=date_end,
        )

    def fake_paid_lot(self, event: Event, amount: int = 10):
        if not isinstance(event, Event):
            raise Exception("'{}' is not instance of Event".format(event))

        return Lot.objects.create(
            event=event,
            price=amount,
            active=True,
            name=self.fake_factory.name(),
            date_start=datetime.now(),
            date_end=event.date_start,
        )

    def fake_private_lot(self, event: Event):
        if not isinstance(event, Event):
            raise Exception("'{}' is not instance of Event".format(event))

        return Lot.objects.create(
            event=event,
            name=self.fake_factory.name(),
            active=True,
            date_start=datetime.now(),
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
            active=True,
            name=self.fake_factory.name(),
            date_start=datetime.now(),
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
    def fake_subscription(lot: Lot, person: Person):
        if not isinstance(lot, Lot):
            raise Exception("'{}' is not instance of Lot".format(lot))

        if not isinstance(person, Person):
            raise Exception("'{}' is not instance of Person".format(person))

        return Subscription.objects.create(
            status=Subscription.CONFIRMED_STATUS,
            lot=lot,
            event=lot.event,
            person=person,
            origin=Subscription.DEVICE_ORIGIN_HOTSITE,
            created_by=0,
            completed=True,
            test_subscription=False,
        )

    @staticmethod
    def fake_test_subscription(lot: Lot, person: Person):
        if not isinstance(lot, Lot):
            raise Exception("'{}' is not instance of Lot".format(lot))

        if not isinstance(person, Person):
            raise Exception("'{}' is not instance of Person".format(person))

        return Subscription.objects.create(
            status=Subscription.CONFIRMED_STATUS,
            lot=lot,
            event=lot.event,
            person=person,
            origin=Subscription.DEVICE_ORIGIN_HOTSITE,
            created_by=0,
            completed=True,
            test_subscription=True,
        )

    @staticmethod
    def fake_unconfirmed_subscription(lot: Lot, person: Person):
        if not isinstance(lot, Lot):
            raise Exception("'{}' is not instance of Lot".format(lot))

        if not isinstance(person, Person):
            raise Exception("'{}' is not instance of Person".format(person))

        return Subscription.objects.create(
            status=Subscription.CONFIRMED_STATUS,
            lot=lot,
            event=lot.event,
            person=person,
            origin=Subscription.DEVICE_ORIGIN_HOTSITE,
            created_by=0,
            completed=False,
            test_subscription=False,
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
