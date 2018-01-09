from django.test import TestCase
from django.urls import reverse


class HomeTest(TestCase):
    def setUp(self):
        self.result = self.client.get(reverse('public:login'))

    def test_status_is_200_ok(self):
        self.assertEqual(self.result.status_code, 200)
