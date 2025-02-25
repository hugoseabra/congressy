""" Testes de aplicação com `Event` - Lista pela view. """
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from gatheros_event.helpers import account
from gatheros_event.models import Event, Organization


class EventListTest(TestCase):
    """ Testes lista de eventos pela view. """
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
        self.url = reverse('event:event-list')

    def _login(self):
        """ Realiza login. """
        self.client.force_login(self.user)

    def _get_active_organization(self):
        request = self.client.request().wsgi_request
        return account.get_organization(request)

    def _get_events(self):
        request = self.client.request().wsgi_request
        organization = account.get_organization(request)
        events = Event.objects.filter(organization=organization)
        return list(events)

    def _switch_context(self):
        organization = self._get_active_organization()
        other = Organization.objects.exclude(pk=organization.pk).filter(
            members__person=self.user.person,
        ).first()

        url = reverse('event:organization-switch')
        self.client.post(url, {'organization-context-pk': other.pk})

    def _get_context_list(self):
        response = self.client.get(self.url)
        event_list = response.context['object_list']
        return list(event_list)

    def test_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        response = self.client.get(self.url, follow=True)

        redirect_url = reverse('public:login')
        redirect_url += '?next=' + self.url
        self.assertRedirects(response, redirect_url)

    def test_status_is_200_ok(self):
        """ Testa se está tudo ok com view com submissão GET. """
        self._login()
        result = self.client.get(self.url)
        self.assertEqual(result.status_code, 200)

    def test_list_of_user_organization(self):
        """ Testa lista de eventos de acordo com a organização do contexto. """

        self._login()
        first_list = self._get_context_list()

        # Primeiro contexto de usuário
        self.assertEqual(first_list, self._get_events())

        # Muda contexto
        self._switch_context()

        # Testa eventos do novo contexto
        self.assertEqual(self._get_context_list(), self._get_events())
        self.assertNotEqual(first_list, self._get_events())
