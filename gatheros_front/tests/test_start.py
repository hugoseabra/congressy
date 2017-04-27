from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class StartTest(TestCase):
    def setUp(self):
        User.objects.create_user('pedro', 'pedro@teste.com', 'password')
        self.client.login(username='pedro', password='password')
        self.result = self.client.get(reverse('gatheros_front:start'))

    def test_status_is_200_ok(self):
        self.assertEqual(self.result.status_code, 200)

    def test_html_contains_email(self):
        self.assertContains(self.result, 'pedro@teste.com')


class StartWithoutLoginTest(TestCase):
    def setUp(self):
        self.result = self.client.get(reverse('gatheros_front:start'))

    def test_redireciona_login(self):
        self.assertEqual(self.result.status_code, 302)
