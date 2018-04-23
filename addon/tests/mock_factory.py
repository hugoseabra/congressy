"""
    Mock factory used during tests to create required objects
"""

from datetime import datetime, timedelta

import random
from django.contrib.auth.models import User
from faker import Faker

from addon.models import OptionalType, Theme, OptionalProduct
from gatheros_event.models import Person, Organization, Event, Category
from gatheros_subscription.models import LotCategory, Subscription


class MockFactory:
    """
        Mock Factory Implementation
    """

    def __init__(self):
        self.fake_factory = Faker()

    def fake_lot_category(self, event=None):
        if not event:
            event = self.fake_event()

        return LotCategory.objects.create(event=event,
                                          name=self.fake_factory.words(
                                              nb=3, ext_word_list=None),
                                          description=self.fake_factory.words(
                                              nb=7, ext_word_list=None)
                                          )

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

    def fake_subscription(self, event=None, person=None):

        if not event:
            event = self.fake_event()

        if not person:
            person = self.fake_person()

        return Subscription.objects.create(
            lot=event.lots.first(),
            event=event,
            person=person,
            created_by=0,
        )

    def fake_optional_type(self):

        return OptionalType.objects.create(
            name=self.fake_factory.words(nb=3, ext_word_list=None),
        )

    def fake_optional_product(self, lot_categories=None, optional_type=None):

        if not lot_categories:
            lot_categories = self.fake_lot_category()

        if not optional_type:
            optional_type = self.fake_optional_type()

        op = OptionalProduct(
            date_end=gen_random_datetime(),
            description='original description',
            quantity=3,
            published=True,
            has_cost=True,
            optional_type=optional_type,
        )

        op.save()
        op.lot_categories.add(lot_categories)
        op.save()

        return op

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
