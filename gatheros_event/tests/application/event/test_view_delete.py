from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from django.http import HttpRequest
from django.test import TestCase
from django.urls import reverse, reverse_lazy

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


class EventDeleteTest(TestCase):
    fixtures = [
        'kanu_locations_city_test',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
        '009_place',
        '010_event',
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

    def _get_url(self, pk=None):
        if not pk:
            event = self._get_event()
            pk = event.pk

        return reverse('gatheros_event:event-delete', kwargs={'pk': pk})

    def test_status_not_allowed_redirects(self):
        result = self.client.get(self._get_url())
        self.assertEqual(result.status_code, 200)

    def test_status_is_200(self):
        member_pks = [member.pk for member in self.user.person.members.all()]
        event = Event.objects.exclude(
            organization__members__in=member_pks
        ).first()
        url = self._get_url(event.pk)

        response = self.client.get(url)
        self.assertRedirects(
            response,
            reverse_lazy('gatheros_event:event-list')
        )

    def test_delete(self):
        response = self.client.post(self._get_url(), follow=True)
        self.assertContains(
            response,
            'Evento excluído com sucesso.'
        )

    def test_cannot_delete(self):
        member_pks = [member.pk for member in self.user.person.members.all()]
        event = Event.objects.exclude(
            organization__members__in=member_pks
        ).first()
        url = self._get_url(event.pk)

        response = self.client.post(url, follow=True)
        self.assertContains(
            response,
            "Você não pode excluir este registro."
        )
