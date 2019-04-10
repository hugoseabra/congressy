"""
    Mock factory used during tests to create required objects
"""

from datetime import datetime, timedelta

from django.contrib.auth.models import User
from faker import Faker

from gatheros_event.models import Organization, Event, Category, Person, Member
from gatheros_subscription.models import Subscription
from ticket.models import Ticket, Lot


class MockFactory:
    """
        Mock Factory Implementation
    """

    def __init__(self):
        self.fake_factory = Faker('pt_BR')

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
            date_start=datetime.now() + timedelta(days=5),
            date_end=datetime.now() + timedelta(days=10),
            category=Category.objects.first(),
        )

    def fake_person(self):
        return Person.objects.create(name=self.fake_factory.name())

    def fake_ticket(self, event=None):

        if event is None:
            event = self.fake_event()

        return Ticket.objects.create(
            event=event,
            name="Ticket: " + self.fake_factory.word(ext_word_list=None)
        )

    def fake_lot(self, ticket: Ticket = None):
        if ticket is None:
            ticket = self.fake_ticket(self.fake_event())

        return Lot.objects.create(
            ticket=ticket,
            name="Lot: " + self.fake_factory.word(ext_word_list=None),
            date_start=datetime.now(),
            date_end=datetime.now() + timedelta(days=1),
        )

    def fake_subscription(self, lot=None, person=None):

        if not person:
            person = self.fake_person()

        if not lot:
            lot = self.fake_lot()

        return Subscription.objects.create(
            ticket_lot=lot,
            event=lot.ticket.event,
            person=person,
            completed=True,
            test_subscription=False,
            created_by=0,
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
