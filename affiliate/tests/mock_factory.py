"""
    Mock factory used during tests to create required objects
"""
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from faker import Faker

from affiliate.models import Affiliate, Affiliation
from gatheros_event.models import Person, Event, Organization, Category
from payment.models import BankAccount


class MockFactory:
    """
        Mock Factory Implementation
    """

    def __init__(self):
        self.fake_factory = Faker()

    def create_fake_person(self):
        person = Person(name=self.fake_factory.name())
        first_name = person.name.split(' ')[0]
        user = User.objects.create_user(
            first_name,
            self.fake_factory.free_email(),
            '123'
        )
        user.save()
        person.user = user
        person.save()

        return person

    def create_fake_bank_account(self):
        return BankAccount.objects.create()

    def create_fake_organization(self):
        return Organization.objects.create(name=self.fake_factory.company())

    def create_fake_event(self, organization=None):

        if not organization:
            organization = self.create_fake_organization()

        if not organization:
            raise Exception('No organization provided for fake event')

        return Event.objects.create(
            organization=organization,
            name='Event: ' + ' '.join(self.fake_factory.words(nb=3)),
            date_start=datetime.now() + timedelta(days=3),
            date_end=datetime.now() + timedelta(days=4),
            category=Category.objects.first(),
        )

    def create_fake_affiliate(self, person=None, bank_account=None):

        if not person:
            person = self.create_fake_person()

        if not bank_account:
            bank_account = self.create_fake_bank_account()

        return Affiliate.objects.create(
            person=person,
            bank_account=bank_account
        )

    def create_fake_affiliation(self, affiliate=None, event=None):

        if not affiliate:
            affiliate = self.create_fake_affiliate()

        if not event:
            event = self.create_fake_event()

        return Affiliation.objects.create(
            affiliate=affiliate,
            event=event,
            percent=5,
            link_whatsapp='link_whatsapp.com',
            link_facebook='link_facebook.com',
            link_twitter='link_twitter.com',
            link_direct='link_direct.com',
        )
