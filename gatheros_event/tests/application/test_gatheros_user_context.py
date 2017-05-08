from django.contrib.auth.models import User
from django.core.exceptions import SuspiciousOperation
from django.test import TestCase

from gatheros_event.acl.gatheros_user_context import UserRequest, \
    clean_user_context, get_user_context, update_user_context, \
    is_user_context_configured
from gatheros_event.models import Member, Organization


class MockSession(object):
    modified = False
    _iter = {}

    def __iter__( self ):
        return iter(self._iter)

    def __getitem__( self, item ):
        return self._iter.get(item)

    def __setitem__( self, key, value ):
        self._iter[key] = value

    def __delitem__( self, key ):
        del self._iter[key]

    def get( self, item ):
        return self._iter.get(item)

    def update( self, data ):
        self._iter.update(data)


class MockRequest(object):
    session = MockSession()

    def __init__( self, pk=4 ):
        self.user = User.objects.get(pk=pk)


class TestGatherosUserContext(TestCase):
    fixtures = [
        '001_user',
        '003_occupation',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
    ]

    def setUp( self ):
        self.request = MockRequest()

    def _test_first_instance_user_context_attributes(
        self,
        user_context,
        user
    ):
        # Usuário logado é o mesmo da sessão
        self.assertEqual(user.pk, user_context.logged_user.pk)

        # Construção de organização e membro no objeto
        member_internal = user.person.members.get(organization__internal=True)
        org_internal = member_internal.organization

        # A organização ativa é a interna, inicialmente
        self.assertEqual(user_context.organization, org_internal)
        self.assertTrue(user_context.active_organization.get('internal'))
        self.assertEqual(
            user_context.active_organization.get('pk'),
            org_internal.pk
        )

        # O membro ativo é o da organização interna inicialmente
        self.assertEqual(
            user_context.active_member_group.get('pk'),
            member_internal.pk
        )
        self.assertEqual(member_internal.group, Member.ADMIN)

        # Membros ligados ao usuário
        user_members_pk = [m.pk for m in user.person.members.all()]
        context_members_pk = [m.get('pk') for m in user_context.members]
        user_members_pk.sort()
        context_members_pk.sort()
        self.assertEqual(user_members_pk, context_members_pk)

    def test_constructor( self ):
        self._test_first_instance_user_context_attributes(
            UserRequest(self.request.user),
            self.request.user
        )

    def test_logged_user_not_superuser( self ):
        uc = UserRequest(self.request.user)
        self.assertFalse(uc.superuser)

    def test_logged_user_superuser( self ):
        request = MockRequest(pk=1)  # Super user
        user_context = UserRequest(request.user)
        self.assertTrue(user_context.superuser)

    def test_get_user_context_logged_user( self ):
        self._test_first_instance_user_context_attributes(
            get_user_context(self.request),
            self.request.user
        )

        self.assertTrue('user_context' in self.request.session)
        keys = [key for key in self.request.session['user_context'].keys()]
        keys.sort()

        self.assertEqual(keys, [
            'active_member_group',
            'active_organization',
            'members',
            'organizations',
            'superuser'
        ])

    def test_update_user_context_allowed_organization_as_member_admin( self ):
        uc = get_user_context(self.request)
        self._test_first_instance_user_context_attributes(uc, self.request.user)
        person = self.request.user.person

        member = person.members.filter(
            organization__internal=False,
            group=Member.ADMIN
        ).first()
        organization = member.organization

        update_user_context(self.request, organization, uc)

        # A organização ativa é a interna, inicialmente
        self.assertEqual(uc.organization, organization)
        self.assertFalse(uc.active_organization.get('internal'))
        self.assertEqual(uc.active_organization.get('pk'), organization.pk)

        # O membro ativo é o da organização interna inicialmente
        self.assertEqual(uc.active_member_group.get('pk'), member.pk)
        self.assertEqual(member.group, Member.ADMIN)

    def test_update_user_context_allowed_organization_as_member_helpre( self ):
        uc = get_user_context(self.request)
        self._test_first_instance_user_context_attributes(uc, self.request.user)
        person = self.request.user.person

        member = person.members.filter(
            organization__internal=False,
            group=Member.HELPER
        ).first()
        organization = member.organization

        update_user_context(self.request, organization, uc)

        # A organização ativa é a interna, inicialmente
        self.assertEqual(uc.organization, organization)
        self.assertFalse(uc.active_organization.get('internal'))
        self.assertEqual(uc.active_organization.get('pk'), organization.pk)

        # O membro ativo é o da organização interna inicialmente
        self.assertEqual(uc.active_member_group.get('pk'), member.pk)
        self.assertEqual(member.group, Member.HELPER)

    def test_update_user_context_not_allowed_organization( self ):
        uc = get_user_context(self.request)
        self._test_first_instance_user_context_attributes(uc, self.request.user)
        person = self.request.user.person

        organization = Organization.objects.exclude(
            members__person=person
        ).first()

        with self.assertRaises(SuspiciousOperation):
            update_user_context(self.request, organization, uc)

    def test_clean_user_context( self ):
        uc = get_user_context(self.request)
        self._test_first_instance_user_context_attributes(uc, self.request.user)

        self.assertTrue('user_context' in self.request.session)
        keys = [key for key in self.request.session['user_context'].keys()]
        keys.sort()

        self.assertEqual(keys, [
            'active_member_group',
            'active_organization',
            'members',
            'organizations',
            'superuser'
        ])

        clean_user_context(self.request)
        self.assertFalse('user_context' in self.request.session)

    def test_is_configured( self ):
        get_user_context(self.request)
        self.assertTrue(is_user_context_configured(self.request))

        clean_user_context(self.request)
        self.assertFalse(is_user_context_configured(self.request))

