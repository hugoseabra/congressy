"""
    Mock factory used during tests to create required objects
"""

import random
from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from faker import Faker

from addon.models import (
    Product,
    Service,
    OptionalType,
    SubscriptionOptionalProduct,
    SubscriptionOptionalService,
    Theme,
)
from gatheros_event.models import Person, Organization, Event, Category
from gatheros_subscription.models import Lot, LotCategory, Subscription


class MockFactory:
    """
        Mock Factory Implementation
    """

    def __init__(self):
        self.fake_factory = Faker()

    def fake_organization(self):
        return Organization.objects.create(name=self.fake_factory.company())

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

    def fake_lot_category(self, event=None):
        if not event:
            event = self.fake_event()

        return LotCategory.objects.create(
            event=event,
            name=self.fake_factory.words(nb=3, ext_word_list=None),
            description=self.fake_factory.words(nb=7, ext_word_list=None)
        )

    def fake_person(self):
        person = Person(name=self.fake_factory.name())
        first_name = person.name.split(' ')[0]
        user = User.objects.create_user(first_name,
                                        self.fake_factory.free_email(),
                                        '123')
        user.save()
        person.user = user
        person.save()

        assert person is not None

        return person

    def fake_lot(self, event=None, lot_category=None):

        if not event:
            event = self.fake_event()

        if not lot_category:
            lot_category = self.fake_lot_category(event=event)

        return Lot.objects.create(
            event=event,
            name='Lot: ' + ' '.join(self.fake_factory.words(nb=3)),
            date_start=datetime.now() + timedelta(days=3),
            date_end=datetime.now() + timedelta(days=4),
            category=lot_category,
        )

    def fake_subscription(self, lot=None, person=None):

        if not person:
            person = self.fake_person()

        if not lot:
            lot = self.fake_lot()

        return Subscription.objects.create(
            lot=lot,
            person=person,
            created_by=0,
        )

    def fake_optional_type(self):

        return OptionalType.objects.create(
            name=self.fake_factory.words(nb=3, ext_word_list=None),
        )

    def fake_product(self, optional_type=None, lot_category=None):

        if not lot_category:
            lot_category = self.fake_lot_category()

        if not optional_type:
            optional_type = self.fake_optional_type()

        date_start = datetime.now() - timedelta(days=3)
        date_end = datetime.now() + timedelta(days=3)

        return Product.objects.create(
            name='optional product',
            optional_type=optional_type,
            lot_category=lot_category,
            date_start=date_start,
            date_end=date_end,
            restrict_unique=False,
        )

    def fake_service(self, optional_type=None, theme=None, lot_category=None):

        if not lot_category:
            lot_category = self.fake_lot_category()

        if not optional_type:
            optional_type = self.fake_optional_type()

        if not theme:
            theme = self.fake_theme()

        date_start = datetime.now() - timedelta(days=3)
        date_end = datetime.now() + timedelta(days=3)

        return Service.objects.create(
            name='optional product',
            optional_type=optional_type,
            theme=theme,
            lot_category=lot_category,
            date_start=date_start,
            date_end=date_end,
            restrict_unique=False,
        )

    def fake_subscription_optional_service(self,
                                           subscription=None,
                                           optional_service=None):
        if not subscription:
            subscription = self.fake_subscription()

        if not optional_service:
            optional_service = self.fake_service(
                lot_category=subscription.lot.category
            )

        return SubscriptionOptionalService.objects.create(
            subscription=subscription,
            optional=optional_service,
        )

    def fake_subscription_optional_product(self,
                                           subscription=None,
                                           optional_product=None):
        if not subscription:
            subscription = self.fake_subscription()

        if not optional_product:
            optional_product = self.fake_product(
                lot_category=subscription.lot.category
            )

        return SubscriptionOptionalProduct.objects.create(
            subscription=subscription,
            optional=optional_product,
        )

    def fake_theme(self):
        return Theme.objects.create(
            name=self.fake_factory.words(nb=3, ext_word_list=None),
        )


def gen_random_datetime(min_year=1900, max_year=datetime.now().year):
    # generate a datetime in format yyyy-mm-dd hh:mm:ss.000000
    start = datetime(min_year, 1, 1, 00, 00, 00)
    years = max_year - min_year + 1
    end = start + timedelta(days=365 * years)
    return start + (end - start) * random.random()
