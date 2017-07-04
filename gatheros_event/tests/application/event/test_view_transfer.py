from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from django.http import HttpRequest
from django.test import TestCase
from django.urls import reverse

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


class EventTransferTest(TestCase):
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
        # Usuário que possui eventos em sua organização interna
        self.user = User.objects.get(username="diegotolentino@gmail.com")
        self.event = Event.objects.get(slug='django-muito-alem-do-python')

    def _login(self):
        """ Realiza login """
        self.client.force_login(self.user)

    def _get_url(self):
        """ Recupera URL """
        pk = self.event.pk
        return reverse('gatheros_event:event-transfer', kwargs={'pk': pk})

    def test_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        response = self.client.get(self._get_url(), follow=True)

        redirect_url = reverse('gatheros_front:login')
        redirect_url += '?next=/'
        self.assertRedirects(response, redirect_url)

    def test_200(self):
        """ Testa se está tudo ok com view com submissão GET. """
        self._login()
        response = self.client.get(self._get_url())
        self.assertEqual(response.status_code, 200)
