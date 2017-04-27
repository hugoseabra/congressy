from django.test import TestCase
from django.urls import  reverse


class InvitationModelTest(TestCase):
    def setUp(self):
        self.result = self.client.get(reverse('gatheros_front:home'))

    def test_status_is_200_ok(self):
        self.assertEqual(self.result.status_code, 200)
