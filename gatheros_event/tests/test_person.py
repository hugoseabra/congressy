from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from kanu_locations.models import City

from ..models import Person


class PersonModelTest(TestCase):
    fixtures = ['005_person_test', '006_organization_test', '007_member_test']

    def test_edit_person_with_invalid_cpf(self):
        person = Person.objects.last()
        person.cpf = '21071332827'

        with self.assertRaises(ValidationError) as e:
            person.save()

        self.assertEqual(dict(e.exception).get('cpf'), ['CPF é inválido'])

    def test_add_person_with_invalid_cpf(self):
        person = Person(
            name="Test",
            genre="M",
            city=City.objects.get(pk=5413),
            cpf="98453217405"
        )

        with self.assertRaises(ValidationError) as e:
            person.save()

        self.assertEqual(dict(e.exception).get('cpf'), ['CPF é inválido'])

    def test_invalid_phone(self):
        person = Person.objects.last()
        person.phone = '985525588584558464 55'

        with self.assertRaises(ValidationError) as e:
            person.save()

        self.assertEqual(dict(e.exception).get('phone'), ['Telefone é inválido'])

    def test_valid_email(self):
        person = Person.objects.last()
        email = 'me@gmail.com'
        person.email = email
        person.save()

        self.assertEqual(person.email, email)

    def test_invalid_email(self):
        person = Person.objects.last()
        person.email = 'gmail.com'

        with self.assertRaises(ValidationError) as e:
            person.save()

        self.assertEqual(dict(e.exception).get('email'), ['Informe um endereço de email válido.'])

        person.email = 'me@gmail.'

        with self.assertRaises(ValidationError) as e:
            person.save()

        self.assertEqual(dict(e.exception).get('email'), ['Informe um endereço de email válido.'])

    def test_has_user_and_not_email(self):
        person = Person.objects.last()
        person.has_user = True

        with self.assertRaises(AttributeError) as e:
            person.save()

        self.assertEqual(str(e.exception), 'Informe o e-mail para vincular um usuário')

    def test_add_remove_user(self):
        person = Person.objects.last()
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
        person = Person.objects.last()
        person.name = 'Another Test'
        person.save()

        organization = person.members.last().organization

        self.assertEqual(person.name, organization.name)

    def test_change_person_user_name(self):
        person = Person.objects.last()
        person.name = 'Another Test'
        person.email = 'me@gmail.com'
        person.has_user = True
        person.save()

        self.assertEqual(person.name, person.user.get_full_name())
