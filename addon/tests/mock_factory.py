"""
    Mock factory used during tests to create required objects
"""

from datetime import datetime, timedelta

from faker import Faker

from addon.models import OptionalType, Theme
from gatheros_event.models import Event, Organization, Category
from gatheros_subscription.models import LotCategory


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

    def fake_optional_type(self):

        return OptionalType.objects.create(
            name=self.fake_factory.words(nb=3, ext_word_list=None),
        )

    def fake_theme(self):
        return Theme.objects.create(
            name=self.fake_factory.words(nb=3, ext_word_list=None),
        )
