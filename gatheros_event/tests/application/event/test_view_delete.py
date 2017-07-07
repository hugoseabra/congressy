from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from django.http import HttpRequest
from django.test import TestCase
from django.urls import reverse

from gatheros_event.helpers import account
from gatheros_event.models import Event


class MockSession(SessionStore):
    def __init__(self):
        super(MockSession, self).__init__()


class MockRequest(HttpRequest):
    def __init__(self, user, session=None):
        self.user = user
        if not session:
            session = MockSession()

        self.session = session
        super(MockRequest, self).__init__()


class EventDeleteTest(TestCase):
    fixtures = [
        'kanu_locations_city_test',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
        '009_place',
        '010_event',
    ]

    def setUp(self):
        self.user = User.objects.get(username="lucianasilva@gmail.com")

    def _login(self):
        """ Realiza login. """
        self.client.force_login(self.user)

    def _get_active_organization(self):
        """ Resgata organização ativa no contexto de usuário. """
        request = MockRequest(self.user, self.client.session)
        return account.get_organization(request)

    def _get_event(self, pk=None):
        """ Resgata instância de Event. """
        if not pk:
            organization = self._get_active_organization()
            return organization.events.first()

        return Event.objects.get(pk=pk)

    def _get_url(self, pk=None):
        """ Resgata URL. """
        if not pk:
            event = self._get_event()
            pk = event.pk

        return reverse('event:event-delete', kwargs={'pk': pk})

    def test_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        response = self.client.get(self._get_url(pk=1), follow=True)

        redirect_url = reverse('front:login')
        redirect_url += '?next=/'
        self.assertRedirects(response, redirect_url)

    def test_200(self):
        """ Testa se está tudo ok com view com submissão GET. """
        self._login()
        response = self.client.get(self._get_url())
        self.assertEqual(response.status_code, 200)

    def test_delete(self):
        self._login()
        response = self.client.post(self._get_url(), follow=True)
        self.assertContains(
            response,
            'Evento excluído com sucesso.'
        )

    def test_cannot_delete(self):
        self._login()
        member_pks = [member.pk for member in self.user.person.members.all()]
        event = Event.objects.exclude(
            organization__members__in=member_pks
        ).first()
        url = self._get_url(event.pk)

        response = self.client.post(url, follow=True)
        self.assertContains(
            response,
            "Você não pode excluir este registro."
        )
