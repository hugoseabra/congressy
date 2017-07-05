from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from gatheros_event.forms import (
    OrganizationForm,
    OrganizationManageMembershipForm,
)
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

    def test_add_internal(self):
        """ Testa adição de nova organização interna. """

        person = self.user.person
        data = person.get_profile_data()
        form = OrganizationForm(user=self.user, internal=True, data=data)
        self.assertTrue(form.is_valid())
        saved_organization = form.save()

        self.assertTrue(saved_organization.internal)

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


class OrganizationManageMembershipFormTest(TestCase):
    """ Testes de formulário de gerenciamento de membros. """

    fixtures = [
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
    ]

    def setUp(self):
        self.user = User.objects.get(email='lucianasilva@gmail.com')
        self.member = self.user.person.members.filter(
            group=Member.ADMIN
        ).first()
        self.form = OrganizationManageMembershipForm(
            organization=self.member.organization
        )

    def _get_other_user(self):
        member = Member.objects.exclude(
            organization=self.member.organization,
            person=self.member.person
        ).first()
        return member.person.user

    def test_activate_not_member(self):
        """
        Testa restrição de se ativar um membro que não seja da organização.
        """
        with self.assertRaises(Exception):
            self.form.activate(self._get_other_user())

    def test_deactivate_not_member(self):
        """
        Testa restrição de se desativar um membro que não seja da organização.
        """
        with self.assertRaises(Exception):
            self.form.activate(self._get_other_user())

    def test_delete_not_member(self):
        """
        Testa restrição de se excluir um membro que não seja da organização.
        """
        with self.assertRaises(Exception):
            self.form.delete(self._get_other_user())

    def test_activate(self):
        """ Testa ativação de membro. """
        self.member.active = False
        self.member.save()

        self.form.activate(self.user)

        member = Member.objects.get(pk=self.member.pk)
        self.assertTrue(member.active)

    def test_deactivate(self):
        """ Testa desativação de membro. """
        self.member.active = True
        self.member.save()

        self.form.deactivate(self.user)

        member = Member.objects.get(pk=self.member.pk)
        self.assertFalse(member.active)

    def test_delete(self):
        """ Testa exclusão de membro. """
        pk = self.member.pk
        self.form.delete(self.user)

        with self.assertRaises(Member.DoesNotExist):
            Member.objects.get(pk=pk)
