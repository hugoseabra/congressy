from django.contrib.auth.models import User
from django.core.exceptions import SuspiciousOperation
from django.test import TestCase

from gatheros_event.helpers import account
from gatheros_event.models import Member, Organization
from gatheros_event.views.mixins import AccountMixin


class MockSession(object):
    modified = False
    _iter = {}

    def __iter__(self):
        return iter(self._iter)

    def __getitem__(self, item):
        return self._iter.get(item)

    def __setitem__(self, key, value):
        self._iter[key] = value

    def __delitem__(self, key):
        del self._iter[key]

    def get(self, item):
        return self._iter.get(item)


class MockRequest(object):
    session = MockSession()

    def __init__(self, user):
        self.user = user


class AccountHelperTest(TestCase):
    fixtures = [
        '001_user',
        '003_occupation',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
    ]

    def _set_user(self, username):
        self.user = User.objects.get(username=username)
        self.request = MockRequest(self.user)
        account.update_account(self.request)

    def _get_organization(self):
        return account.get_organization(self.request)

    def setUp(self):
        self._set_user("lucianasilva@gmail.com")

    def test_account_in_session(self):
        self.assertIn('account', self.request.session)

    def test_by_default_active_organization_is_the_internal(self):
        organization = Organization.objects.get(slug="luciana-silva")
        self.assertEqual(self._get_organization(), organization)

    def test_change_organization(self):
        # Organização inicial
        organization1 = Organization.objects.get(slug="luciana-silva")
        account.set_organization(self.request, organization1)
        self.assertEqual(self._get_organization(), organization1)

        # Organização setada
        organization2 = Organization.objects.get(slug="mnt")
        account.set_organization(self.request, organization2)
        self.assertEqual(self._get_organization(), organization2)

    def test_when_is_organization_changed_change_member_too(self):
        # Membro da organização 1
        organization1 = Organization.objects.get(slug="luciana-silva")
        member1 = Member.objects.get(organization=organization1,
                                     person=self.user.person)
        account.set_organization(self.request, organization1)
        self.assertEqual(account.get_member(self.request), member1)

        # Membro da organização 2
        organization2 = Organization.objects.get(slug="mnt")
        member2 = Member.objects.get(organization=organization2,
                                     person=self.user.person)
        account.set_organization(self.request, organization2)
        self.assertEqual(account.get_member(self.request), member2)

    def test_return_organizations_of_user_logged(self):
        # Organizações do usuário 1
        organizations1 = list(
            Organization.objects.filter(members__person=self.user.person)
        )

        self.assertListEqual(
            account.get_organizations(self.request),
            organizations1
        )

        # Organizações do usuário 2
        self._set_user("flavia@in2web.com.br")
        organizations2 = list(
            Organization.objects.filter(members__person=self.user.person)
        )

        self.assertListEqual(
            account.get_organizations(self.request),
            organizations2
        )

        # Organizações são diferentes
        def compare_lists(list1, list2):
            if len(list1) != len(list2):
                return False
            for item in list1:
                if item not in list2:
                    return False
            return True

        self.assertTrue(compare_lists(organizations1, organizations1))
        self.assertFalse(compare_lists(organizations1, []))
        self.assertFalse(compare_lists(organizations1, organizations2))

    def test_clear_account(self):
        account.get_member(self.request)
        account.get_organization(self.request)
        account.get_organizations(self.request)

        # Os caches estão estabelecidos na requisição
        self.assertTrue(hasattr(self.request, '_cached_organization'))
        self.assertTrue(hasattr(self.request, '_cached_member'))
        self.assertTrue(hasattr(self.request, '_cached_organizations'))

        # Executa o clean
        account.clean_account(self.request)

        # Account apagada da sessão
        self.assertNotIn('account', self.request.session)

        # Os caches apagados da requisição
        self.assertFalse(hasattr(self.request, '_cached_organization'))
        self.assertFalse(hasattr(self.request, '_cached_member'))
        self.assertFalse(hasattr(self.request, '_cached_organizations'))

    def test_user_without_person(self):
        with self.assertRaises(SuspiciousOperation):
            self._set_user('kanu')


class AccountHelperIsConfiguredTest(TestCase):
    fixtures = [
        '001_user',
        '003_occupation',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
    ]

    def setUp(self):
        self.user = User.objects.get(username="lucianasilva@gmail.com")
        self.request = MockRequest(self.user)
        account.clean_account(self.request)

    def test_configured_on_login(self):
        self.assertFalse(account.is_configured())
        self.client.login(testcase_user=self.user)
        self.assertTrue(account.is_configured())

    def test_configured_on_update_account(self):
        self.assertFalse(account.is_configured())
        account.update_account(self.request)
        self.assertTrue(account.is_configured())

    def test_not_configured_after_clean_account(self):
        self.assertFalse(account.is_configured())
        account.update_account(self.request)
        self.assertTrue(account.is_configured())
        account.clean_account(self.request)
        self.assertFalse(account.is_configured())


class AccountMixinTest(TestCase):
    fixtures = [
        '001_user',
        '003_occupation',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
    ]

    def setUp(self):
        self.user = User.objects.get(username="lucianasilva@gmail.com")
        self.client.login(testcase_user=self.user)
        self.view = AccountMixin(request=self.client.request().wsgi_request)

    def test_organizations(self):
        self.assertTrue(hasattr(self.view, 'organizations'))
        self.assertEqual(
            self.view.organizations,
            account.get_organizations(self.client.request().wsgi_request)
        )

    def test_organization(self):
        self.assertTrue(hasattr(self.view, 'organization'))
        self.assertEqual(
            self.view.organization,
            account.get_organization(self.client.request().wsgi_request)
        )

    def test_member(self):
        self.assertTrue(hasattr(self.view, 'member'))
        self.assertEqual(
            self.view.member,
            account.get_member(self.client.request().wsgi_request)
        )
