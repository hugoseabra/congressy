from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from gatheros_event.forms import OrganizationForm
from gatheros_event.models import Member, Organization


# @TODO Testar upload de avatar

class OrganizationFormTest(TestCase):
    """ Testes de organization form """

    fixtures = [
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
    ]

    def setUp(self):
        self.user = User.objects.get(email='lucianasilva@gmail.com')

    def test_add(self):
        """ Testa adição de nova organização. """

        data = {'name': 'New Organization'}

        form = OrganizationForm(user=self.user, data=data)
        self.assertTrue(form.is_valid())
        form.save()

        persisted_org = Organization.objects.filter(
            name__contains=data['name']
        ).first()
        self.assertFalse(persisted_org.internal)
        self.assertTrue(persisted_org.active)

        members = persisted_org.members.filter(person=self.user.person)
        self.assertTrue(members.count() > 0)

        member = members.first()
        self.assertEqual(member.group, Member.ADMIN)

    def test_error_user_not_member(self):
        organization = Organization.objects.get(slug='paroquias-unidas')

        with self.assertRaises(ValidationError) as e:
            OrganizationForm(user=self.user, instance=organization)
            self.assertEqual(
                e.exception,
                {'__all__': 'Usuário não possui qualquer vínculo com a'
                            ' organização.'}
            )

    def test_edit(self):
        organization = Organization.objects.get(
            slug='in2-web-solucoes-e-servicos',
            internal=False
        )

        data = {
            'name': organization.name + ' edited',
            'description_html': 'description inserted'
        }

        form = OrganizationForm(
            instance=organization,
            user=self.user,
            data=data
        )
        self.assertTrue(form.is_valid())
        saved_org = form.save()
        self.assertFalse(saved_org.internal)

        organization = Organization.objects.get(pk=saved_org.pk)

        self.assertEqual(organization.name, data['name'])
        self.assertEqual(
            organization.description_html,
            data['description_html']
        )
