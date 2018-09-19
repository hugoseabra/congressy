"""
    Mock factory used during tests to create required gatheros event
    domain objects.
"""
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from faker import Faker

from gatheros_event.models import Person, Event, Organization, Category, Member, Info


class MockFactory:
    """
        Mock Factory Implementation
    """

    def __init__(self):
        self.fake_factory = Faker('pt_BR')

    def fake_person(self):
        person = Person(name=self.fake_factory.name(),
                        email=self.fake_factory.free_email())

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
        return Organization.objects.create(
            name=self.fake_factory.company(),
            email=self.fake_factory.ascii_email(),
        )

    def fake_paying_organization(self):
        org = self.fake_organization()
        org.bank_code = Organization.BANCO_DO_BRASIL
        org.agency = '001'
        org.account = '001'
        org.cnpj_ou_cpf = '36876747034'
        org.account_type = Organization.CONTA_CORRENTE
        org.save()
        return org

    def fake_event(self, organization=None, date_start=None, date_end=None):

        if date_start is None:
            date_start = datetime.now() + timedelta(days=3)

        if date_end is None:
            date_end = datetime.now() + timedelta(days=4)

        if not organization:
            organization = self.fake_organization()

        event = Event.objects.create(
            name='Event: ' + ' '.join(self.fake_factory.words(nb=3)),
            organization=organization,
            date_start=date_start,
            date_end=date_end,
            category=Category.objects.first(),
        )

        Info.objects.create(
            event=event
        )

        return event

    @staticmethod
    def join_organization(organization, person):

        membership = Member(person=person, organization=organization,
                            group=Member.ADMIN)
        membership.save()

        return membership
