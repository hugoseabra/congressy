"""
    Mock factory used during tests to create required objects
"""
from datetime import datetime, timedelta

from faker import Faker

from gatheros_event.models import Person, Event, Organization, Category
from partner.models import Partner, PartnerPlan


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

    def _create_fake_person(self):
        person = Person(name=self.fake_factory.name())
        person.save()
        return person

    def _create_fake_organization(self):
        organization = Organization(name=self.fake_factory.company())
        organization.save()
        return organization

    def _create_fake_partner(self, person=None):

        if not person:
            person = self.person

        partner = Partner(person=person)
        partner.save()
        return partner

    def _create_fake_partner_plan(self):
        name = 'Partner Plan: ' + ' '.join(self.fake_factory.words(nb=2))
        partner_plan = PartnerPlan(name=name, percent=5.5)
        partner_plan.save()
        return partner_plan

    def _create_fake_event(self, organization=None):

        if not organization:
            organization = self.organization

        event = Event(
            organization=organization,
            name='Event: ' + ' '.join(self.fake_factory.words(nb=3)),
            date_start=datetime.now() + timedelta(days=3),
            date_end=datetime.now() + timedelta(days=4),
            category=Category.objects.first(),
        )
        event.save()
        return event
