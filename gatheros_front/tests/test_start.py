from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class StartTest(TestCase):
    fixtures = [
        '001_user',
        '003_occupation',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
    ]

    def setUp(self):
        self.user = User.objects.get(username='lucianasilva@gmail.com')
        self.client.force_login(self.user)
        self.result = self.client.get(reverse('gatheros_front:start'))

    def test_status_is_200_ok(self):
        self.assertEqual(self.result.status_code, 200)

    def test_html_contains_email(self):
        self.assertContains(self.result, self.user.email)


class StartWithoutLoginTest(TestCase):
    def setUp(self):
        self.result = self.client.get(reverse('gatheros_front:start'))

    def test_redireciona_login(self):
        self.assertEqual(self.result.status_code, 302)
