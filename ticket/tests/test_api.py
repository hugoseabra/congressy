from datetime import datetime, timedelta

from django.test import TestCase
from rest_framework.test import APIClient

from gatheros_subscription.models import Subscription
from ticket.tests import MockFactory


class TicketAPITest(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.url = '/api/ticket/tickets/'
        self.mock_factory = MockFactory()
        self.unauthenticated_client = APIClient()
        self.authenticated_client = APIClient()
        self.organizer_client = APIClient()
        self.event = self.mock_factory.fake_event()

        self.authenticated_client.force_authenticate(
            user=self.mock_factory.fake_user()
        )

        self.organizer_client.force_authenticate(
            user=self.mock_factory.fake_organizer(event=self.event).user
        )

    def test_create(self):
        payload = {'name': 'random name',
                   'event': self.event.pk,
                   'free_installments': 10, }

        request = self.unauthenticated_client.post(
            self.url,
            payload,
            format='json'
        )

        # User is not authenticated.
        self.assertEqual(request.status_code, 403)

        request = self.authenticated_client.post(
            self.url,
            payload,
            format='json'
        )

        # User is authenticated, but is not an organizer.
        self.assertEqual(request.status_code, 403)

        request = self.organizer_client.post(
            self.url,
            payload,
            format='json'
        )

        # User is authenticated and is an organizer.
        self.assertEqual(request.status_code, 201)

    def test_read(self):
        instance = self.mock_factory.fake_ticket(event=self.event)

        url = self.url + str(instance.pk) + '/'

        request = self.unauthenticated_client.get(url)

        # User is not authenticated.
        self.assertEqual(request.status_code, 403)

        request = self.authenticated_client.get(url)

        # User is authenticated, but is not an organizer.
        self.assertEqual(request.status_code, 403)

        request = self.organizer_client.get(url)

        # User is authenticated and is an organizer.
        self.assertEqual(request.status_code, 200)

    def test_list(self):
        instance = self.mock_factory.fake_ticket(event=self.event)

        request = self.unauthenticated_client.get(self.url)

        # User is not authenticated.
        self.assertEqual(request.status_code, 403)

        request = self.authenticated_client.get(self.url)

        # User is authenticated, but is not an organizer.
        self.assertEqual(request.status_code, 200)
        self.assertNotIn(bytes(instance.name, 'utf8'), request.content)

        request = self.organizer_client.get(self.url)

        # User is authenticated and is an organizer.
        self.assertEqual(request.status_code, 200)
        self.assertIn(bytes(instance.name, 'utf8'), request.content)

    def test_partial_update(self):
        instance = self.mock_factory.fake_ticket(event=self.event)

        url = self.url + str(instance.pk) + '/'

        payload = {'name': 'new name'}

        request = self.unauthenticated_client.patch(url, payload, format='json')

        # User is not authenticated.
        self.assertEqual(request.status_code, 403)

        request = self.authenticated_client.patch(url, payload, format='json')

        # User is authenticated, but is not an organizer.
        self.assertEqual(request.status_code, 403)

        request = self.organizer_client.patch(url, payload, format='json')

        # User is authenticated and is an organizer.
        self.assertEqual(request.status_code, 200)
        self.assertIn(bytes('new name', 'utf8'), request.content)

    def test_update(self):
        instance = self.mock_factory.fake_ticket(event=self.event)

        url = self.url + str(instance.pk) + '/'

        payload = {
            'name': 'new name',
            'event': self.event.pk,
            'free_installments': 5,
        }

        request = self.unauthenticated_client.put(url, payload, format='json')

        # User is not authenticated.
        self.assertEqual(request.status_code, 403)

        request = self.authenticated_client.put(url, payload, format='json')

        # User is authenticated, but is not an organizer.
        self.assertEqual(request.status_code, 403)

        request = self.organizer_client.put(url, payload, format='json')

        # User is authenticated and is an organizer.
        self.assertEqual(request.status_code, 200)
        self.assertIn(bytes('new name', 'utf8'), request.content)

        payload['event'] = self.mock_factory.fake_event().pk

        new_event = self.mock_factory.fake_event()
        payload['event'] = new_event.pk

        request = self.organizer_client.put(url, payload, format='json')

        # User is authenticated and is an organizer of event that is editing,
        # but not of the new event.
        self.assertEqual(request.status_code, 400)

    def test_delete(self):
        instance = self.mock_factory.fake_ticket(event=self.event)
        lot = self.mock_factory.fake_lot(instance)

        url = self.url + str(instance.pk) + '/'

        request = self.unauthenticated_client.delete(url)

        # User is not authenticated.
        self.assertEqual(request.status_code, 403)

        request = self.authenticated_client.delete(url)

        # User is authenticated, but is not an organizer.
        self.assertEqual(request.status_code, 403)

        sub = self.mock_factory.fake_subscription(lot=lot)
        sub.status = Subscription.CONFIRMED_STATUS
        sub.save()

        request = self.organizer_client.delete(url)

        # User is authenticated and is an organizer.
        self.assertEqual(request.status_code, 409)

        sub.delete()

        request = self.organizer_client.delete(url)
        self.assertEqual(request.status_code, 204)


class LotAPITest(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.url = '/api/ticket/lots/'
        self.mock_factory = MockFactory()
        self.unauthenticated_client = APIClient()
        self.authenticated_client = APIClient()
        self.organizer_client = APIClient()
        self.event = self.mock_factory.fake_event()
        self.ticket = self.mock_factory.fake_ticket(self.event)

        self.authenticated_client.force_authenticate(
            user=self.mock_factory.fake_user()
        )

        self.organizer_client.force_authenticate(
            user=self.mock_factory.fake_organizer(event=self.event).user
        )

    def test_create(self):
        payload = {
            'ticket': self.ticket.pk,
            'name': 'lot #1',
            'date_start': datetime.now(),
            'date_end': datetime.now() + timedelta(days=1)
        }

        request = self.unauthenticated_client.post(
            self.url,
            payload,
            format='json'
        )

        # User is not authenticated.
        self.assertEqual(request.status_code, 403)

        request = self.authenticated_client.post(
            self.url,
            payload,
            format='json'
        )

        # User is authenticated, but is not an organizer.
        self.assertEqual(request.status_code, 403)

        request = self.organizer_client.post(
            self.url,
            payload,
            format='json'
        )

        # User is authenticated and is an organizer.
        self.assertEqual(request.status_code, 201)

    def test_read(self):
        instance = self.mock_factory.fake_lot(self.ticket)

        url = self.url + str(instance.pk) + '/'

        request = self.unauthenticated_client.get(url)

        # User is not authenticated.
        self.assertEqual(request.status_code, 403)

        request = self.authenticated_client.get(url)

        # User is authenticated, but is not an organizer.
        self.assertEqual(request.status_code, 403)

        request = self.organizer_client.get(url)

        # User is authenticated and is an organizer.
        self.assertEqual(request.status_code, 200)

    def test_list(self):
        instance = self.mock_factory.fake_lot(self.ticket)

        request = self.unauthenticated_client.get(self.url)

        # User is not authenticated.
        self.assertEqual(request.status_code, 403)

        request = self.authenticated_client.get(self.url)

        # User is authenticated, but is not an organizer.
        self.assertEqual(request.status_code, 200)
        self.assertNotIn(bytes(instance.name, 'utf8'), request.content)

        request = self.organizer_client.get(self.url)

        # User is authenticated and is an organizer.
        self.assertEqual(request.status_code, 200)
        self.assertIn(bytes(instance.name, 'utf8'), request.content)

    def test_partial_update(self):
        instance = self.mock_factory.fake_lot(self.ticket)

        url = self.url + str(instance.pk) + '/'

        payload = {'name': 'new name'}

        request = self.unauthenticated_client.patch(url, payload, format='json')

        # User is not authenticated.
        self.assertEqual(request.status_code, 403)

        request = self.authenticated_client.patch(url, payload, format='json')

        # User is authenticated, but is not an organizer.
        self.assertEqual(request.status_code, 403)

        request = self.organizer_client.patch(url, payload, format='json')

        # User is authenticated and is an organizer.
        self.assertEqual(request.status_code, 200)
        self.assertIn(bytes('new name', 'utf8'), request.content)

    def test_update(self):
        instance = self.mock_factory.fake_lot(self.ticket)

        url = self.url + str(instance.pk) + '/'

        payload = {
            'ticket': self.ticket.pk,
            'name': 'new name',
            'date_start': datetime.now(),
            'date_end': datetime.now() + timedelta(days=2)
        }

        request = self.unauthenticated_client.put(url, payload, format='json')

        # User is not authenticated.
        self.assertEqual(request.status_code, 403)

        request = self.authenticated_client.put(url, payload, format='json')

        # User is authenticated, but is not an organizer.
        self.assertEqual(request.status_code, 403)

        request = self.organizer_client.put(url, payload, format='json')

        # User is authenticated and is an organizer.
        self.assertEqual(request.status_code, 200)
        self.assertIn(bytes('new name', 'utf8'), request.content)

        payload['ticket'] = self.mock_factory.fake_ticket().pk
        request = self.organizer_client.put(url, payload, format='json')

        # User is authenticated and is an organizer of event that is editing,
        # but not of the new event.
        self.assertEqual(request.status_code, 400)

    def test_delete(self):
        instance = self.mock_factory.fake_lot(self.ticket)

        url = self.url + str(instance.pk) + '/'

        request = self.unauthenticated_client.delete(url)

        # User is not authenticated.
        self.assertEqual(request.status_code, 403)

        request = self.authenticated_client.delete(url)

        # User is authenticated, but is not an organizer.
        self.assertEqual(request.status_code, 403)

        sub = self.mock_factory.fake_subscription(instance)
        sub.status = Subscription.CONFIRMED_STATUS
        sub.save()

        request = self.organizer_client.delete(url)

        # User is authenticated and is an organizer.
        self.assertEqual(request.status_code, 409)

        sub.delete()

        request = self.organizer_client.delete(url)
        self.assertEqual(request.status_code, 204)
