from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse, resolve
from uuid import uuid4
from .views import PostBackView


class TaskTest(TestCase):

    def test_GET_request(self):
        response = self.client.get('/api/payments/pagarme/postback/' + str(uuid4()), follow=True)
        self.assertEqual(response.status_code, 405)

    def test_POST_request(self):

        #response_match = resolve('/api/payments/pagarme/postback/' + str(uuid4()))

        response = self.client.post('/api/payments/pagarme/postback/' + str(uuid4()), follow=True)
        self.assertEqual(response.resolver_match.func.__name__, PostBackView.as_view().__name__)
        self.assertEqual(response.status_code, 200)
