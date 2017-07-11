from django.contrib.auth.models import User
from django.test import TestCase

from gatheros_event.helpers import account
from gatheros_event.models import Member, Organization
from gatheros_event.views.mixins import AccountMixin


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
        account.clean_account(self.client.request().wsgi_request)

    def test_configured_on_login(self):
        """ Testa configuração após o login. """
        request = self.client.request().wsgi_request
        self.assertFalse(account.is_configured(request))
        self.client.force_login(self.user)

        # Login utiliza outro objeto de session. Recriando para resgatar dados.
        self.assertTrue(account.is_configured(request))

    def test_configured_on_update_account(self):
        """ Testa configuração após a atualização de conta. """
        request = self.client.request().wsgi_request
        self.assertFalse(account.is_configured(request))
        account.update_account(request)
        self.assertTrue(account.is_configured(request))

    def test_not_configured_after_clean_account(self):
        """ Testa configuração após limpeza de dados de conta. """
        request = self.client.request().wsgi_request
        self.assertFalse(account.is_configured(request))
        account.update_account(request)
        self.assertTrue(account.is_configured(request))
        account.clean_account(request)
        self.assertFalse(account.is_configured(request))


class BaseAccountHelperTest(TestCase):
    fixtures = [
        '001_user',
        '005_user',
        '003_occupation',
        '006_person',
        '007_organization',
        '008_member',
    ]

    def setUp(self):
        self.organization = Organization.objects.first()

    # noinspection PyMethodMayBeStatic
    def _get_user_no_person(self):
        """ Resgata instância de usuário sem vínculo com `Person`. """
        return User.objects.get(username='kanu')

    # noinspection PyMethodMayBeStatic
    def _get_user_not_manager(self):
        """
        Resgata instância de usuário que não possui organização.
        """
        return User.objects.get(email='marcela@gmail.com')

    # noinspection PyMethodMayBeStatic
    def _get_user_only_internal(self):
        """
        Resgata instância de um usuário possui apenas organização interna.
        """
        return User.objects.get(email='diegotolentino@gmail.com')

    # noinspection PyMethodMayBeStatic
    def _get_user_no_internal(self):
        """
        Resgata instância de usuário que não possui organização interna, mas
        possui organizações externas.
        """
        return User.objects.get(email='hugoseabra19@gmail.com')

    # noinspection PyMethodMayBeStatic
    def _get_user_normal(self):
        """
        Resgata usuário que possui organização interna e outras externas.
        """
        return User.objects.get(email='lucianasilva@gmail.com')


class AccountHelperTest(BaseAccountHelperTest):
    def test_account_in_session(self):
        """ Testa se sessão possui informações de conta. """
        user = self._get_user_normal()
        self.client.force_login(user)

        request = self.client.request().wsgi_request
        self.assertIn('account', request.session)

    def test_by_default_active_organization_is_the_internal(self):
        """
        Testa se usuário possui organização interna, ela deve ser a primeira a
        ser ativa.
        """
        # Organização interna.
        user = self._get_user_normal()
        self.client.force_login(user)

        request = self.client.request().wsgi_request
        member = user.person.members.get(organization__internal=True)
        assert member is not None

        org = member.organization
        self.assertEqual(account.get_organization(request), org)

    def test_not_logged(self):
        """ Testa funções de helper sem usuário logado. """
        request = self.client.request().wsgi_request

        account.update_account(request)
        account.update_account(request, self.organization)

        self.assertFalse(account.is_eligible(request))
        self.assertFalse(account.is_manager(request))
        self.assertEqual(account.get_organizations(request), [])
        self.assertIsNone(account.get_organization(request))

        # Mesmo forçando atualização, nada acontece
        account.set_active_organization(request, self.organization)
        self.assertIsNone(account.get_organization(request))

    def test_user_no_person(self):
        """ Testa funções a partir de um usuário sem vínculo com `Person`."""
        user = self._get_user_no_person()
        self.client.force_login(user)

        request = self.client.request().wsgi_request

        account.update_account(request)
        account.update_account(request, self.organization)

        self.assertFalse(account.is_eligible(request))
        self.assertFalse(account.is_manager(request))
        self.assertEqual(account.get_organizations(request), [])
        self.assertIsNone(account.get_organization(request))

        # Mesmo forçando atualização, nada acontece
        account.set_active_organization(request, self.organization)
        self.assertIsNone(account.get_organization(request))

    def test_user_not_manager(self):
        """
        Testa funções a partir de um usuário que não é Organizador, ou seja,
        que não possui relação com qualquer membro de organização.
        """
        user = self._get_user_not_manager()
        self.client.force_login(user)

        request = self.client.request().wsgi_request

        account.update_account(request)

        self.assertTrue(account.is_eligible(request))
        self.assertFalse(account.is_manager(request))
        self.assertEqual(account.get_organizations(request), [])
        self.assertIsNone(account.get_organization(request))

        # Mesmo forçando atualização, nada acontece
        account.set_active_organization(request, self.organization)
        self.assertIsNone(account.get_organization(request))

        # Força atualização e nada muda.
        account.update_account(request, self.organization)

        self.assertTrue(account.is_eligible(request))
        self.assertFalse(account.is_manager(request))
        self.assertEqual(account.get_organizations(request), [])
        self.assertIsNone(account.get_organization(request))

        # Mesmo forçando atualização, nada acontece
        account.set_active_organization(request, self.organization)
        self.assertIsNone(account.get_organization(request))

    def test_user_only_internal(self):
        """
        Testa funções a partir de um usuário que não é Organizador, ou seja,
        que não possui relação com qualquer membro de organização.
        """
        user = self._get_user_only_internal()
        self.client.force_login(user)

        member = user.person.members.first()
        organization = member.organization
        self.assertTrue(organization.internal)

        request = self.client.request().wsgi_request

        account.update_account(request)

        self.assertTrue(account.is_eligible(request))
        self.assertTrue(account.is_manager(request))
        self.assertEqual(account.get_organizations(request), [organization])

        active_org = account.get_organization(request)
        self.assertIsInstance(active_org, Organization)
        self.assertEqual(active_org.pk, organization.pk)

    def test_user_no_internal(self):
        """
        Testa funções a partir de um usuário que é Organizador mas não possi
        organização interna.
        """
        user = self._get_user_no_internal()
        self.client.force_login(user)

        person = user.person
        members = person.members.filter(active=True, organization__active=True)
        orgs = [m.organization for m in members]

        # Não possui organização interna
        internal = [org.pk for org in orgs if org.internal]
        self.assertEqual(internal, [])

        request = self.client.request().wsgi_request

        account.update_account(request)

        self.assertTrue(account.is_eligible(request))
        self.assertTrue(account.is_manager(request))

        context_orgs = account.get_organizations(request)
        for org in orgs:
            self.assertIn(org, context_orgs)

        active_org = account.get_organization(request)
        self.assertIsInstance(active_org, Organization)
        self.assertIn(active_org, orgs)

        # Atualiza pegando a última organização
        last_org = orgs[-1]
        account.update_account(request, last_org)
        active_org = account.get_organization(request)
        self.assertIsInstance(active_org, Organization)
        self.assertEqual(active_org.pk, last_org.pk)

    def test_user_normal(self):
        """
        Testa funções a partir de um usuário que é Organizador, possuindo
        organizações internas e externas.
        """
        user = self._get_user_normal()
        self.client.force_login(user)

        person = user.person
        members = person.members.filter(active=True, organization__active=True)
        orgs = [m.organization for m in members]

        # Não possui organização interna
        internal = [org.pk for org in orgs if org.internal]
        self.assertEqual(len(internal), 1)

        request = self.client.request().wsgi_request
        account.update_account(request)

        self.assertTrue(account.is_eligible(request))
        self.assertTrue(account.is_manager(request))

        context_orgs = account.get_organizations(request)
        for org in orgs:
            self.assertIn(org, context_orgs)

        active_org = account.get_organization(request)
        self.assertIsInstance(active_org, Organization)
        self.assertIn(active_org, orgs)

        # Atualiza pegando a última organização
        last_org = orgs[-1]
        account.update_account(request, last_org)
        active_org = account.get_organization(request)
        self.assertIsInstance(active_org, Organization)
        self.assertEqual(active_org.pk, last_org.pk)

    def test_change_organization(self):
        """ Testa mudança de organização ativa. """
        # Organização inicial
        user = self._get_user_normal()
        self.client.force_login(user)

        request = self.client.request().wsgi_request

        organization1 = Organization.objects.get(slug="luciana-silva")
        account.set_active_organization(request, organization1)
        self.assertEqual(account.get_organization(request), organization1)

        # Organização setada
        organization2 = Organization.objects.get(slug="mnt")
        account.set_active_organization(request, organization2)
        self.assertEqual(account.get_organization(request), organization2)

    def test_change_member(self):
        """
        Testa quando organização organização ativa muda, o membro também muda.
        """
        user = self._get_user_normal()
        self.client.force_login(user)

        request = self.client.request().wsgi_request

        # Membro da organização 1
        organization1 = Organization.objects.get(slug="luciana-silva")
        member1 = Member.objects.get(
            organization=organization1,
            person=user.person
        )
        account.set_active_organization(request, organization1)
        self.assertEqual(account.get_member(request), member1)

        # Membro da organização 2
        organization2 = Organization.objects.get(slug="mnt")
        member2 = Member.objects.get(
            organization=organization2,
            person=user.person
        )
        account.set_active_organization(request, organization2)
        self.assertEqual(account.get_member(request), member2)

    def test_get_organizations(self):
        """ Testa retorno de lista de organizações do usuáro logado. """
        user = self._get_user_normal()
        self.client.force_login(user)

        request = self.client.request().wsgi_request

        # Organizações do usuário 1
        organizations1 = list(account.get_organizations(request))

        self.assertListEqual(
            account.get_organizations(request),
            organizations1
        )

        # Organizações do usuário 2
        user = User.objects.get(email='flavia@in2web.com.br')
        self.client.force_login(user)
        request = self.client.request().wsgi_request

        organizations2 = list(account.get_organizations(request))

        self.assertListEqual(
            account.get_organizations(request),
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
        self.assertFalse(compare_lists(organizations1, organizations2))

    def test_clear_account(self):
        """ Testa limpeza de dados de conta do usuário no contexto. """
        user = self._get_user_normal()
        self.client.force_login(user)

        request = self.client.request().wsgi_request

        account.get_member(request)
        account.get_organization(request)
        account.get_organizations(request)

        # Os caches estão estabelecidos na requisição
        self.assertTrue(hasattr(request, 'cached_organization'))
        self.assertTrue(hasattr(request, 'cached_member'))
        self.assertTrue(hasattr(request, 'cached_organizations'))

        # Executa o clean
        account.clean_account(request)

        # Account apagada da sessão
        self.assertNotIn('account', request.session)

        # Os caches apagados da requisição
        self.assertFalse(hasattr(request, 'cached_organization'))
        self.assertFalse(hasattr(request, 'cached_member'))
        self.assertFalse(hasattr(request, 'cached_organizations'))


class AccountMixinViewTest(TestCase):
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
        self.client.force_login(self.user)
        self.view = AccountMixin(request=self.client.request().wsgi_request)

    def test_is_authenticated(self):
        """ Testa se existe propriedade `is_authenticated` em view. """
        self.assertTrue(hasattr(self.view, 'is_authenticated'))
        self.assertEqual(
            self.view.is_authenticated,
            self.user.is_authenticated()
        )

    def test_is_manager(self):
        """ Testa se existe propriedade `is_manager` em view. """
        self.assertTrue(hasattr(self.view, 'is_manager'))
        self.assertEqual(
            self.view.is_manager,
            account.is_manager(self.client.request().wsgi_request)
        )

    def test_organizations(self):
        """ Testa se existe propriedade `organizations` em view. """
        self.assertTrue(hasattr(self.view, 'organizations'))
        self.assertEqual(
            self.view.organizations,
            account.get_organizations(self.client.request().wsgi_request)
        )

    def test_organization(self):
        """ Testa se existe propriedade `organization` em view. """
        self.assertTrue(hasattr(self.view, 'organization'))
        self.assertEqual(
            self.view.organization,
            account.get_organization(self.client.request().wsgi_request)
        )

    def test_member(self):
        """ Testa se existe propriedade `member` em view. """
        self.assertTrue(hasattr(self.view, 'member'))
        self.assertEqual(
            self.view.member,
            account.get_member(self.client.request().wsgi_request)
        )

    def test_has_internal_organization(self):
        """
        Testa se existe propriedade `has_internal_organization` em view.
        """
        self.assertTrue(hasattr(self.view, 'has_internal_organization'))
        orgs = [
            org for org in self.view.organizations if org.is_admin(self.user)
        ]
        has_internal = len(orgs) > 0

        self.assertEqual(self.view.has_internal_organization, has_internal)
