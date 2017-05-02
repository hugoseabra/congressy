from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class LoginTest(TestCase):
    def setUp(self):
        self.data = {
            'username': 'pedro',
            'password': 'password'
        }
        User.objects.create_user(**self.data)

    def test_get_login_is_200_ok(self):
        self.result = self.client.get(reverse('gatheros_front:login'))
        self.assertEqual(self.result.status_code, 200)

    def test_if_login_ok_redirect(self):
        self.client.login(**self.data)
        self.result = self.client.get(reverse('gatheros_front:login'))
        self.assertRedirects(self.result, reverse('gatheros_front:start'))

    def test_check_login_ok(self):
        self.result = self.client.post(reverse('gatheros_front:login'),
                                       data=self.data)
        self.assertRedirects(self.result, reverse('gatheros_front:start'))

    def test_check_login_fail(self):
        data = self.data
        data['username'] = 'jose'
        self.result = self.client.post(reverse('gatheros_front:login'),
                                       data=data)
        self.assertEqual(self.result.status_code, 200)
        self.assertContains(self.result, 'errornote')
