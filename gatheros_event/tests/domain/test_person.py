from django.contrib.auth.models import User
from django.test import TestCase
from kanu_locations.models import City

from gatheros_event.models import Member, Person


class PersonModelTest(TestCase):
    fixtures = [
        'kanu_locations_city_test',
        '003_occupation',
        '004_category',
        '005_user',
        '006_person',
        '007_organization',
        '008_member'
    ]

    # noinspection PyMethodMayBeStatic
    def _get_person_with_no_user(self):
        return Person.objects.get(pk='e50e56e7-2686-497f-82b1-a2500243f12b')

    # noinspection PyMethodMayBeStatic
    def _get_person_with_internal_organization(self):
        return Person.objects.get(pk='a7c5f518-7669-4b71-a83b-2a7107e9c313')

    # noinspection PyMethodMayBeStatic
    def _get_person_with_external_organization(self):
        return Person.objects.get(pk='5c76d747-f22a-4d27-9211-3b9929fb908d')

    def _create_person(self, persist=True, **kwargs):
        data = {
            'name': 'Test',
            'gender': 'M',
            'city': City.objects.get(pk=5413)
        }
        data.update(kwargs)
        entity = Person(**data)

        if persist:
            entity.save()

        return entity

    def test_muda_nome_de_pessoa_e_de_organizacao(self):
        # Test if internal organization name is edited
        person = self._get_person_with_internal_organization()
        person.name = 'Edited name'
        person.save()

        member = person.members.filter(organization__internal=True).first()
        self.assertIsNotNone(member)

        organization = member.organization

        self.assertEqual(member.group, Member.ADMIN)
        self.assertEqual(person.name, organization.name)

        # Test if external organization name is edited
        person = self._get_person_with_external_organization()

        member = person.members.filter(group=Member.ADMIN,
                                       organization__internal=False).first()
        self.assertIsNotNone(member)

        person.name = 'Edited name'
        person.save()

        organization = member.organization
        org_name = organization.name

        self.assertNotEqual(person.name, organization.name)
        self.assertNotEqual(person.name, org_name)

    def test_muda_nome_de_pessoa_e_de_usuario(self):
        user = User.objects.create_user('me@gmail.com')
        person = self._create_person(
            name='Another Test',
            email='me@gmail.com',
            user=user
        )
        self.assertIsNotNone(person.user)
        self.assertEqual(person.name, person.user.get_full_name())

        person.name = 'Edited name'
        person.save()
        self.assertEqual(person.name, person.user.get_full_name())
