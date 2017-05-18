from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from django.http import HttpRequest
from django.test import TestCase
from django.urls import reverse

from gatheros_event.helpers import account
from gatheros_event.models import Event, Organization, Member


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


class AddEventTest(TestCase):
    fixtures = [
        'kanu_locations_city_test',
        '005_user',
        '003_occupation',
        '004_category',
        '006_person',
        '007_organization',
        '008_member',
        '009_place',
        '010_event',
    ]

    def setUp(self):
        # Usuário com várias organizações
        self.user = User.objects.get(username="lucianasilva@gmail.com")
        self.url = reverse('gatheros_event:event-add')
        self.client.login(testcase_user=self.user)

    def test_status_is_200_ok(self):
        result = self.client.get(self.url)
        self.assertEqual(result.status_code, 200)


class EditEventTest(TestCase):
    fixtures = [
        'kanu_locations_city_test',
        '005_user',
        '003_occupation',
        '004_category',
        '006_person',
        '007_organization',
        '008_member',
        '009_place',
        '010_event',
    ]

    def setUp(self):
        # Usuário com várias organizações
        self.user = User.objects.get(username="lucianasilva@gmail.com")
        self.client.login(testcase_user=self.user)

    def _get_active_organization(self):
        request = MockRequest(self.user, self.client.session)
        return account.get_organization(request)

    def _get_event(self):
        organization = self._get_active_organization()
        return Event.objects.filter(organization=organization).first()

    def _get_url(self, pk=None):
        if not pk:
            event = self._get_event()
            pk = event.pk

        return reverse('gatheros_event:event-edit', kwargs={'pk': pk})

    def _switch_context(self, group=Member.ADMIN):
        organization = self._get_active_organization()
        other = Organization.objects.exclude(pk=organization.pk).filter(
            members__person=self.user.person,
            members__group=group
        ).first()

        url = reverse('gatheros_event:organization-switch')
        self.client.post(url, {'organization-context-pk': other.pk})

    def test_user_can_edit(self):
        result = self.client.get(self._get_url())
        self.assertEqual(result.status_code, 200)

    def test_user_cannot_edit(self):
        event = self._get_event()

        # Usuário não está em nenhuma das organizações do usuário inicial
        self.user = User.objects.get(username="diegotolentino@gmail.com")
        self.client.login(testcase_user=self.user)

        # Tenta editar evento no qual não possui acesso
        result = self.client.get(self._get_url(pk=event.pk))
        self.assertEqual(result.status_code, 302)
        self.assertRedirects(result, reverse('gatheros_event:event-list'))
