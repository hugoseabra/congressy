from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class LoginTest(TestCase):
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

    def test_get_login_is_200_ok(self):
        self.result = self.client.get(reverse('front:login'))
        self.assertEqual(self.result.status_code, 200)

    def test_if_login_ok_redirect(self):
        self.client.force_login(self.user)
        self.result = self.client.get(reverse('front:login'))
        self.assertRedirects(self.result, reverse('front:start'))

    def test_check_login_ok(self):
        password = '12345'
        self.user.set_password(password)
        self.user.save()
        data = {
            'username': self.user.username,
            'password': password
        }
        self.result = self.client.post(
            reverse('event:login'),
            data=data
        )
        self.assertRedirects(self.result, reverse('front:start'))

    def test_check_login_fail(self):
        data = {
            'username': 'jose que nao existe',
            'password': 'senha'
        }
        self.result = self.client.post(
            reverse('front:login'),
            data=data
        )
        self.assertEqual(self.result.status_code, 200)
        self.assertContains(self.result, 'errornote')
