"""
    Mock factory used during tests to create required objects
"""

from datetime import datetime, timedelta

from django.contrib.auth.models import User
from faker import Faker

from gatheros_event.models import Organization, Event, Category, Person, Member
from ticket.models import Ticket


class MockFactory:
    """
        Mock Factory Implementation
    """

    def __init__(self):
        self.fake_factory = Faker()

    def fake_organization(self):
        return Organization.objects.create(
            name=self.fake_factory.company(),
            internal=False,
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

    def fake_person(self):
        return Person.objects.create(name=self.fake_factory.name())

    def fake_ticket(self, event=None, user=None):

        if event is None:
            event = self.fake_event()

        if user is None:
            user = self.fake_user()

        members = [m.person.user for m in
                   event.organization.members.filter(active=True)]

        if not hasattr(user, 'person'):
            person = self.fake_person()
            user.person = person
            user.save()

        if user not in members:
            p = user.person
            self.fake_membership(organization=event.organization, person=p)

        return Ticket.objects.create(
            event=event,
            created_by=user,
            name=self.fake_factory.word(ext_word_list=None)
        )

    def fake_user(self):
        return User.objects.create(
            username=self.fake_factory.simple_profile()['username']
        )

    def fake_membership(self, organization, person):
        return Member.objects.create(
            group=Member.ADMIN,
            person=person,
            active=True,
            organization=organization,
        )
