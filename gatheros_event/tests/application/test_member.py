# test_edit_type_resend_invitation
# membro_deve_possuir_um_convite_antes_de_existir


# test_internal_edition_not_allowed

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ImproperlyConfigured

from gatheros_event.models import Member, Organization


class OrganizationAdminNotInternalPermissionsTest(TestCase):
    fixtures = [
        '003_occupation',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
    ]

    def setUp(self):
        self.user = User.objects.get(username='flavia@in2web.com.br')
        self.organization = Organization.objects.get(slug="paroquias-unidas")

    def test_admin_can_delete(self):
        self.assertTrue(self.organization.is_admin(self.user))
        self.assertTrue(self.user.has_perm(
            'gatheros_event.delete_member',
            self.organization.members.first()
        ))


class MemberManageViewTest(TestCase):
    fixtures = [
        '003_occupation',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
    ]

    def setUp(self):
        self.user = User.objects.get(username='flavia@in2web.com.br')
        self.client.force_login(self.user)

    def _get_member(self, group=None):
        """
        Recupera um membro que não seja de organização interna e não seja do
        usuário logado.
        """
        user_members = self.user.person.members.filter(group=Member.ADMIN)
        user_member = user_members.filter(organization__internal=False).first()

        organization = user_member.organization
        member = organization.members.exclude(pk=user_member.pk)

        if group:
            member = member.filter(group=group)

        return member.first()

    def test_delete(self):
        member = self._get_member()
        organization = member.organization

        url = reverse('gatheros_event:member-delete', kwargs={
            'organization_pk': organization.pk,
            'pk': member.pk
        })
        response = self.client.post(url, follow=True)
        self.assertContains(response, 'Membro excluído com sucesso.')

        with self.assertRaises(Member.DoesNotExist):
            Member.objects.get(pk=member.pk)

    def test_activate(self):
        member = self._get_member()
        organization = member.organization

        member.active = False
        member.save()

        url = reverse('gatheros_event:member-manage', kwargs={
            'organization_pk': organization.pk,
            'pk': member.pk
        })

        data = {
            'action': 'activate'
        }

        response = self.client.post(url, data, follow=True)
        self.assertContains(response, 'Membro alterado com sucesso.')

        member = Member.objects.get(pk=member.pk)
        self.assertTrue(member.active)

    def test_deactivate(self):
        member = self._get_member()
        organization = member.organization

        member.active = True
        member.save()

        url = reverse('gatheros_event:member-manage', kwargs={
            'organization_pk': organization.pk,
            'pk': member.pk
        })

        data = {
            'action': 'deactivate'
        }

        response = self.client.post(url, data, follow=True)
        self.assertContains(response, 'Membro alterado com sucesso.')

        member = Member.objects.get(pk=member.pk)
        self.assertFalse(member.active)

    def test_change_group_wrong_group(self):
        member = self._get_member(group=Member.ADMIN)
        organization = member.organization

        self.assertEqual(member.group, Member.ADMIN)

        url = reverse('gatheros_event:member-manage', kwargs={
            'organization_pk': organization.pk,
            'pk': member.pk
        })

        data = {
            'action': 'change_group',
            'group': 'any'
        }

        with self.assertRaises(ImproperlyConfigured) as e:
            self.client.post(url, data)
            self.assertContains(
                e,
                'Campo `group` não encontrado ou vazio.'
                ' Para alterar o grupo do membro você precisa informar um'
                ' grupo válido. Os grupos podem ser: admin, helper.'
            )

    def test_change_group(self):
        member = self._get_member(group=Member.ADMIN)
        organization = member.organization

        self.assertEqual(member.group, Member.ADMIN)

        url = reverse('gatheros_event:member-manage', kwargs={
            'organization_pk': organization.pk,
            'pk': member.pk
        })

        data = {
            'action': 'change_group',
            'group': Member.HELPER
        }

        response = self.client.post(url, data, follow=True)
        self.assertContains(
            response,
            'Membro alterado com sucesso.'
        )

        member = Member.objects.get(pk=member.pk)
        self.assertEqual(member.group, Member.HELPER)
