from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
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

    def test_edit_person_with_invalid_cpf(self):
        person = Person.objects.last()
        person.cpf = '21071332827'

        with self.assertRaises(ValidationError) as e:
            person.save()

        self.assertTrue('cpf' in dict(e.exception).keys())

    def test_add_person_with_invalid_cpf(self):
        person = Person(
            name="Test",
            genre="M",
            city=City.objects.get(pk=5413),
            cpf="98453217405"
        )

        with self.assertRaises(ValidationError) as e:
            person.save()

        self.assertTrue('cpf' in dict(e.exception).keys())

    def test_invalid_phone(self):
        person = Person.objects.last()
        person.phone = '985525588584558464 55'

        with self.assertRaises(ValidationError) as e:
            person.save()

        self.assertTrue('phone' in dict(e.exception).keys())

    def test_valid_email(self):
        person = Person.objects.last()
        email = 'me@gmail.com'
        person.email = email
        person.save()

        self.assertEqual(person.email, email)

    def test_invalid_email(self):
        person = Person.objects.first()
        person.email = 'gmail.com'

        with self.assertRaises(ValidationError) as e:
            person.save()

        self.assertTrue('email' in dict(e.exception).keys())

        person.email = 'me@gmail.'
        with self.assertRaises(ValidationError) as e:
            person.save()

        self.assertTrue('email' in dict(e.exception).keys())

    def test_has_user_and_not_email(self):
        person = Person.objects.last()
        person.has_user = True

        with self.assertRaises(ValidationError) as e:
            person.save()

        self.assertTrue('email' in dict(e.exception).keys())

    def test_add_remove_user(self):
        person = Person.objects.first()
        person.has_user = True
        person.email = 'me@gmail.com'
        person.save()

        user = User.objects.get(username=person.email)

        self.assertEqual(user, person.user)
        self.assertEqual(user.email, person.email)

        person.has_user = False
        person.save()

        self.assertIsNone(person.user)

    def test_change_person_organization_name(self):
        person = Person.objects.get(pk='a7c5f518-7669-4b71-a83b-2a7107e9c313')
        person.name = 'Another Test'
        person.save()

        member = person.members.first()
        organization = member.organization

        self.assertEqual(member.group, Member.ADMIN)
        self.assertEqual(person.name, organization.name)

    def test_change_person_user_name(self):
        person = Person.objects.first()
        person.name = 'Another Test'
        person.email = 'me@gmail.com'
        person.has_user = True
        person.save()

        self.assertEqual(person.name, person.user.get_full_name())
