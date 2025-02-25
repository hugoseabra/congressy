"""
Testes de aplicação com `Organization` - Mudança de organização no contexto.
"""
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from gatheros_event.helpers import account
from gatheros_event.models import Organization


class OrganizationSwitchTest(TestCase):
    """ Testes de mudança de organização contexto pela view. """
    fixtures = [
        'kanu_locations_city_test',
        '005_user',
        '003_occupation',
        '004_category',
        '006_person',
        '007_organization',
        '008_member',
        '009_place',
        '010_event',
    ]

    def setUp(self):
        # Usuário com várias organizações
        self.user = User.objects.get(username="lucianasilva@gmail.com")
        self.client.force_login(self.user)
        self.url = reverse('event:organization-switch')

    def _get_organization(self, wsgi_request=None):
        if wsgi_request is None:
            wsgi_request = self.client.request().wsgi_request
        return account.get_organization(wsgi_request)

    def _get_organization_other(self, organization):
        orgs = account.get_organizations(self.client.request().wsgi_request)
        assert len(orgs) > 1

        return [org for org in orgs if org.pk != organization.pk][0]

    def _get_organization_not_member(self):
        orgs = account.get_organizations(self.client.request().wsgi_request)
        return Organization.objects \
            .exclude(pk__in=[org.pk for org in orgs]) \
            .first()

    def test_get_redirect_302(self):
        org = self._get_organization()
        result = self.client.get(self.url, {'organization-context-pk': org.pk})
        self.assertEqual(result.status_code, 302)

    def test_switch_organization(self):
        """ Testa mudança de organização. """
        # First organization
        organization1 = self._get_organization()

        # Switch
        other = self._get_organization_other(organization1).pk
        result = self.client.post(self.url, {'organization-context-pk': other})

        # Check if changed
        organization2 = self._get_organization(result.wsgi_request)
        self.assertEqual(other, organization2.pk)

    def test_not_allowed_organization_403(self):
        """ Testa restrição quando mudança de organização não é permitida. """
        org = self._get_organization_not_member()
        response = self.client.post(
            self.url,
            {'organization-context-pk': org.pk},
            follow=True
        )
        self.assertContains(response, 'Você não é membro desta organização.')

    def test_not_exist_organization_404(self):
        """ Testa restrição para mudança para uma organização inexistente"""
        response = self.client.post(
            self.url, {'organization-context-pk': 9999999},
            follow=True
        )
        self.assertEqual(response.status_code, 404)

    def test_presentation(self):
        """ Testa mensagem de sucesso ao mudar organização no contexto. """
        # First organization
        organization = self._get_organization()
        response = self.client.post(
            self.url,
            {'organization-context-pk': organization.pk}
        )
        messages = [m for m in get_messages(response.wsgi_request)]
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            "Agora você não está em organização.",
            str(messages[0])
        )

        # Second organization
        organization = self._get_organization_other(organization)
        response = self.client.post(
            self.url,
            {'organization-context-pk': organization.pk}
        )
        messages = [m for m in get_messages(response.wsgi_request)]
        self.assertEqual(len(messages), 1)
        self.assertInHTML(
            "Agora você está na organização '%s'." % organization.name,
            str(messages[0])
        )
