import datetime

from django.db import IntegrityError
from django.test import TestCase
from kanu_locations.models import City

from gatheros_event.models import Member, Organization, Person


class OrganizationModelTest(TestCase):
    fixtures = [
        'kanu_locations_city_test',
        '003_occupation',
        '004_category',
        '005_user',
        '006_person',
        '007_organization',
        '008_member'
    ]

    def test_internal_organization_only_one_member(self):
        organization = Organization.objects.first()

        self.assertTrue(organization.internal)

        person = Person.objects.create(
            name="Person Test",
            genre="M",
            city=City.objects.get(pk=5413),
            cpf="28488214421"
        )

        with self.assertRaises(IntegrityError):
            Member.objects.create(
                organization=organization,
                person=person,
                group=Member.ADMIN,
                created_by=1,
                invited_on=datetime.datetime.now()
            )

    def test_internal_member_is_admin(self):
        """
        Mesmo tendo selecionado um outro grupo que não ADMIN, organizações internas
        sempre terão seu membro principal como ADMIN
        """
        person = Person.objects.create(
            name="Person Test",
            genre="M",
            city=City.objects.get(pk=5413),
            cpf="28488214421",
            has_user=True,
            email='test@test.me'
        )
        # Person has user
        self.assertIsNotNone(person.user)

        organization = Organization.objects.create(name=person.name, internal=True)

        # Trying to insert member as HELPER in internal organization
        with self.assertRaises(IntegrityError):
            Member.objects.create(
                organization=organization,
                person=person,
                group=Member.HELPER,
                created_by=1,
                invited_on=datetime.datetime.now()
            )

    def test_member_with_no_user_not_allowed(self):
        person = Person.objects.create(
            name="Person Test",
            genre="M",
            city=City.objects.get(pk=5413),
            cpf="28488214421",
            has_user=False
        )
        self.assertIsNone(person.user)

        organization = Organization.objects.create(name=person.name, internal=True)

        # Trying to insert member from a person without USER
        with self.assertRaises(IntegrityError):
            Member.objects.create(
                organization=organization,
                person=person,
                group=Member.ADMIN,
                created_by=1,
                invited_on=datetime.datetime.now()
            )

    def test_internal_org_must_have_member(self):
        person = Person.objects.get(pk='a7c5f518-7669-4b71-a83b-2a7107e9c313')
        member = person.members.first()

        with self.assertRaises(IntegrityError):
            member.delete()
