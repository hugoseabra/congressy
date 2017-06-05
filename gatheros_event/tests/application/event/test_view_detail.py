import os

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from django.http import HttpRequest
from django.test import TestCase
from django.urls import reverse
from django.utils import six

from gatheros_event.helpers import account
from gatheros_event.models import Event, Member, Organization


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


class EventDetailUrl(TestCase):
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
        self.event = Event.objects.get(slug='seo-e-resultados')
        self.url = reverse('gatheros_event:event-detail', kwargs={
            'pk': self.event.pk
        })

    def login(self):
        self.client.force_login(self.user)
        self._switch_context()

    def _get_active_organization(self):
        request = MockRequest(self.user, self.client.session)
        return account.get_organization(request)

    def _switch_context(self, group=Member.ADMIN):
        organization = self._get_active_organization()
        other = Organization.objects.exclude(pk=organization.pk).filter(
            members__person=self.user.person,
            members__group=group
        ).first()
        url = reverse('gatheros_event:organization-switch')
        self.client.post(url, {'organization-context-pk': other.pk})

    def test_status_is_302(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        login = reverse('gatheros_front:login')+'?next='+self.url
        self.assertRedirects(response, login)

    def test_status_authenticated_200(self):
        self.login()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class EventDetailUploadTest(TestCase):
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
        self.path = os.path.join(settings.MEDIA_ROOT, 'test')

        self.user = User.objects.get(username="lucianasilva@gmail.com")
        self.client.force_login(self.user)
        self._switch_context()

    def _get_active_organization(self):
        request = MockRequest(self.user, self.client.session)
        return account.get_organization(request)

    def _switch_context(self, group=Member.ADMIN):
        organization = self._get_active_organization()
        other = Organization.objects.exclude(pk=organization.pk).filter(
            members__person=self.user.person,
            members__group=group
        ).first()
        url = reverse('gatheros_event:organization-switch')
        self.client.post(url, {'organization-context-pk': other.pk})

    def _get_url(self, pk=None):
        if not pk:
            event = self._get_event()
            pk = event.pk

        return reverse('gatheros_event:event-detail', kwargs={
            'pk': pk
        })

    # noinspection PyMethodMayBeStatic
    def _get_event(self):
        return Event.objects.get(slug='seo-e-resultados')

    def test_upload(self):
        file_names = {
            'banner_top': 'Evento_Banner_topo.png',
            'banner_slide': 'Evento_Banner_destaque.png',
            'banner_small': 'Evento_Banner_pequeno.png',
        }

        files_dict = {}
        for field_name, file_name in six.iteritems(file_names):
            file_path = os.path.join(self.path, file_name)
            file = open(file_path, 'rb')
            files_dict[field_name] = file

        files_dict['submit_type'] = 'update_banners'
        response = self.client.post(self._get_url(), files_dict, follow=True)
        self.assertContains(response, 'Banners atualizados com sucesso.')

        event = self._get_event()
        for field_name, file_name in six.iteritems(file_names):
            file = getattr(event, field_name)
            name = file.name
            file_path = os.path.join(settings.MEDIA_ROOT, file_name)

            self.assertEqual(name, file_name)
            self.assertTrue(os.path.isfile(file_path))

        # Clear file deve limpar o campo no model e deletar os arquivos
        data_dict = {
            'submit_type': 'update_banners'
        }
        for field_name in six.iterkeys(file_names):
            key = field_name + '-clear'
            data_dict[key] = 'on'

        response = self.client.post(self._get_url(), data_dict, follow=True)
        self.assertContains(response, 'Banners atualizados com sucesso.')

        # Campos limpos e sem arquivos
        event = self._get_event()
        for field_name, file_name in six.iteritems(file_names):
            assert hasattr(event, field_name)
            attr = getattr(event, field_name)
            file_path = os.path.join(settings.MEDIA_ROOT, file_name)

            # Campo ImageFile deve ter o arquivo enviado.
            self.assertEqual(attr.name, '')
            self.assertFalse(os.path.isfile(file_path))
