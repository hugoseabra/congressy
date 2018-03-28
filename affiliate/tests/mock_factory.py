"""
    Mock factory used during tests to create required objects
"""
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from faker import Faker

from gatheros_event.models import Person, Event, Organization, Category


class MockFactory:
    """
        Mock Factory Implementation
    """

    def __init__(self):
        self.fake_factory = Faker()

    organization = None
    person = None
    partner = None
    partner_plan = None
    event = None
    user = None

    def _create_fake_person(self):
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

    def _create_fake_organization(self):
        organization = Organization(name=self.fake_factory.company())
        organization.save()

        assert organization is not None

        return organization

    def _create_fake_event(self, organization=None):

        if not organization:
            organization = self.organization

        if not organization:
            raise Exception('No organization provided for fake event')

        event = Event(
            organization=organization,
            name='Event: ' + ' '.join(self.fake_factory.words(nb=3)),
            date_start=datetime.now() + timedelta(days=3),
            date_end=datetime.now() + timedelta(days=4),
            category=Category.objects.first(),
        )
        event.save()

        assert event is not None

        return event
