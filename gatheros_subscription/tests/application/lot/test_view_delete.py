from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from django.http import HttpRequest
from django.test import TestCase
from django.urls import reverse

from gatheros_event.helpers import account
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


class LotDeleteTest(TestCase):
    fixtures = [
        'kanu_locations_city_test',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
        '009_place',
        '010_event',
        '005_lot',
    ]

    def setUp(self):
        self.user = User.objects.get(username="lucianasilva@gmail.com")
        self.client.force_login(self.user)

    def _get_active_organization(self):
        request = MockRequest(self.user, self.client.session)
        return account.get_organization(request)

    def _get_event(self, pk=None):
        if not pk:
            organization = self._get_active_organization()
            return organization.events.first()

        return Event.objects.get(pk=pk)

    def _get_url(self, event_pk, pk):
        if not pk:
            event = self._get_event()
            pk = event.pk

        return reverse(
            'gatheros_event:lot-delete',
            kwargs={'event_pk': event_pk, 'lot_pk': pk}
        )
