""" Testes de aplicação com `Organization` - Painel. """
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from gatheros_event.models import Organization


class EventPanelTest(TestCase):
    """ Testes de painel de organização pela view. """
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
        self.user = User.objects.get(username="lucianasilva@gmail.com")
        self.org = Organization.objects.get(
            slug='in2-web-solucoes-e-servicos'
        )

    def _login(self):
        """ Realiza login """
        self.client.force_login(self.user)

    def _get_url(self):
        """ Recupera URL """
        pk = self.org.pk
        return reverse('event:organization-panel', kwargs={'pk': pk})

    def test_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        response = self.client.get(self._get_url(), follow=True)

        redirect_url = reverse('front:login')
        redirect_url += '?next=/'
        self.assertRedirects(response, redirect_url)

    def test_200(self):
        """ Testa se está tudo ok com view com submissão GET. """
        self._login()
        response = self.client.get(self._get_url())
        self.assertEqual(response.status_code, 200)
