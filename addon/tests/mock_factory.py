"""
    Mock factory used during tests to create required objects
"""

from decimal import Decimal
import random
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from faker import Faker

from addon.models import (
    OptionalProduct,
    OptionalService,
    OptionalType,
    ProductPrice,
    ServicePrice,
    SubscriptionOptionalProduct,
    SubscriptionOptionalService,
    Theme,
)
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

        lot = event.lots.first()
        lot.category = self.fake_lot_category(event=lot.event)
        lot.save()

        return Subscription.objects.create(
            lot=lot,
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
            lot_categories = [self.fake_lot_category()]

        if not optional_type:
            optional_type = self.fake_optional_type()

        date_start = datetime.now() - timedelta(days=3)
        date_end = datetime.now() + timedelta(days=3)

        op = OptionalProduct(
            date_start=date_start,
            date_end=date_end,
            description='original description',
            quantity=3,
            optional_type=optional_type,
        )

        op.save()

        for lot_category in lot_categories:
            op.lot_categories.add(lot_category)

        op.save()

        return op

    def fake_optional_service(self, lot_categories=None, optional_type=None,
                              theme=None):

        if not lot_categories:
            lot_categories = [self.fake_lot_category()]

        if not optional_type:
            optional_type = self.fake_optional_type()

        if not theme:
            theme = self.fake_theme()

        date_start = datetime.now() - timedelta(days=3)
        date_end = datetime.now() + timedelta(days=3)

        os = OptionalService(
            date_start=date_start,
            date_end=date_end,
            description='original description',
            quantity=3,
            theme=theme,
            optional_type=optional_type,
        )

        os.save()

        for lot_category in lot_categories:
            os.lot_categories.add(lot_category)

        os.save()

        return os

    def fake_service_price(self, lot_category=None, optional_service=None):
        if not lot_category:
            lot_category = self.fake_lot_category()

        if not optional_service:
            optional_service = self.fake_optional_service(
                lot_categories=[lot_category]
            )

        date_start = datetime.now() - timedelta(days=3)
        date_end = datetime.now() + timedelta(days=3)

        return ServicePrice.objects.create(
            date_start=date_start,
            date_end=date_end,
            price=Decimal(20.00),
            lot_category=lot_category,
            optional_service=optional_service,
        )

    def fake_product_price(self, lot_category=None, optional_product=None):
        if not lot_category:
            lot_category = self.fake_lot_category()

        if not optional_product:
            optional_product = self.fake_optional_product(
                lot_categories=[lot_category]
            )

        date_start = datetime.now() - timedelta(days=3)
        date_end = datetime.now() + timedelta(days=3)

        return ProductPrice.objects.create(
            date_start=date_start,
            date_end=date_end,
            price=Decimal(20.00),
            lot_category=lot_category,
            optional_product=optional_product,
        )

    def fake_subscription_optional_service(self,
                                           subscription=None,
                                           optional_service=None):
        if not subscription:
            subscription = self.fake_subscription()

        if not optional_service:
            optional_service = self.fake_optional_service(
                lot_categories=[subscription.lot.category]
            )

        return SubscriptionOptionalService.objects.create(
            subscription=subscription,
            optional_service=optional_service,
            price=Decimal(20.00),
            count=1,
            total_allowed=20,
        )

    def fake_subscription_optional_product(self,
                                           subscription=None,
                                           optional_product=None):
        if not subscription:
            subscription = self.fake_subscription()

        if not optional_product:
            optional_product = self.fake_optional_product(
                lot_categories=[subscription.lot.category]
            )

        return SubscriptionOptionalProduct.objects.create(
            subscription=subscription,
            optional_product=optional_product,
            price=Decimal(20.00),
            count=1,
            total_allowed=20,
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
