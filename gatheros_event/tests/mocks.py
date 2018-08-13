"""
    Mock factory used during tests to create required gatheros event
    domain objects.
"""
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from faker import Faker

from gatheros_event.models import Person, Event, Organization, Category, Member


class MockFactory:
    """
        Mock Factory Implementation
    """

    def __init__(self):
        self.fake_factory = Faker('pt_BR')

    def fake_person(self):
        person = Person(name=self.fake_factory.name(), email=self.fake_factory.free_email())

        first_name = person.name.split(' ')[0]
        email = person.email
        password = 'password'
        user = User.objects.create_user(first_name=first_name,
                                        username=email,
                                        email=email,
                                        password=password)
        user.save()
        person.user = user
        person.save()

        assert person is not None

        return person

    def fake_organization(self):
        organization = Organization(
            name=self.fake_factory.company(),
            email=self.fake_factory.ascii_email(),
        )
        organization.save()

        assert organization is not None

        return organization

    def fake_event(self, organization=None):

        if not organization:
            organization = self.fake_organization()

        return Event.objects.create(
            name='Event: ' + ' '.join(self.fake_factory.words(nb=3)),
            organization=organization,
            date_start=datetime.now() + timedelta(days=3),
            date_end=datetime.now() + timedelta(days=4),
            category=Category.objects.first(),
        )

    @staticmethod
    def join_organization(organization, person):

        membership = Member(person=person, organization=organization,
                            group=Member.ADMIN)
        membership.save()

        return membership

