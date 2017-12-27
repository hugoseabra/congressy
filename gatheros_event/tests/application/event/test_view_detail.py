""" Testes de aplicação com `Event` - Detalhes de evento. """
import os
import shutil

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import six

from gatheros_event.helpers import account
from gatheros_event.models import Event, Member, Organization


class EventDetailBannersUploadTest(TestCase):
    """ Testes de upload de banners nos detalhes de evento pela view. """
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
        self.file_base_path = os.path.join(
            settings.BASE_DIR,
            'gatheros_event',
            'tests',
            'fixtures',
            'media',
            'event'
        )
        self.event_path = os.path.join(settings.MEDIA_ROOT, 'event')
        self.persisted_path = 'event'

        self.user = User.objects.get(username="lucianasilva@gmail.com")

    def _login(self):
        """ Realiza login. """
        self.client.force_login(self.user)
        self._clear_uploaded_directory()
        self._switch_context()

    def _get_active_organization(self):
        """ Resgata organização ativa no contexto de usuário. """
        return account.get_organization(self.client.request().wsgi_request)

    def _switch_context(self, group=Member.ADMIN):
        """ Muda organização do contexto de usuário. """
        organization = self._get_active_organization()
        other = Organization.objects.exclude(pk=organization.pk).filter(
            members__person=self.user.person,
            members__group=group
        ).first()
        url = reverse('event:organization-switch')
        self.client.post(url, {'organization-context-pk': other.pk})

    def _get_url(self, pk=None):
        """ Resgata URL. """
        if not pk:
            event = self._get_event()
            pk = event.pk

        return reverse('event:event-detail', kwargs={
            'pk': pk
        })

    # noinspection PyMethodMayBeStatic
    def _get_event(self):
        """ Resgata instância de Event. """
        org = self._get_active_organization()
        return org.events.first()

    # noinspection PyMethodMayBeStatic
    def _clear_uploaded_directory(self):
        """ Exclui diretório de upload com todos os arquivos. """
        event = self._get_event()
        path = os.path.join(self.event_path, str(event.pk))
        if os.path.isdir(path):
            shutil.rmtree(path)

    def tearDown(self):
        """
        Limpa arquivos enviados se há organização no contexto do usuário.
        """
        org = account.get_organization(self.client.request().wsgi_request)
        # Se não tiver organização no contexto, não precisa limpar o diretório
        if org:
            self._clear_uploaded_directory()

    def test_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        response = self.client.get(self._get_url(1), follow=True)

        redirect_url = reverse('front:login')
        redirect_url += '?next='
        redirect_url += self._get_url(1)
        self.assertRedirects(response, redirect_url)

    def test_200(self):
        """ Testa se está tudo ok com view com submissão GET. """
        self._login()
        response = self.client.get(self._get_url())
        self.assertEqual(response.status_code, 200)

    def test_upload(self):
        """ Testa upload de banners. """
        self._login()
        file_names = {
            'banner_top': 'Evento_Banner_topo.png',
            'banner_slide': 'Evento_Banner_destaque.png',
            'banner_small': 'Evento_Banner_pequeno.png',
        }

        files_dict = {}
        for field_name, file_name in six.iteritems(file_names):
            file_path = os.path.join(self.file_base_path, file_name)
            file = open(file_path, 'rb')
            files_dict[field_name] = file

        files_dict['submit_type'] = 'update_banners'
        response = self.client.post(self._get_url(), files_dict, follow=True)
        self.assertContains(response, 'Banners atualizados com sucesso.')

        event = self._get_event()
        for field_name, file_name in six.iteritems(file_names):
            file = getattr(event, field_name)

            file_dir = os.path.join(self.event_path, str(event.pk))
            file_path = os.path.join(file_dir, file_name)

            self.assertEqual(file.name, '{}/{}/{}'.format(
                self.persisted_path,
                str(event.pk),
                file_name
            ))
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

            file_dir = os.path.join(self.event_path, str(event.pk))
            file_path = os.path.join(file_dir, file_name)

            # Campo ImageFile deve ter o arquivo enviado.
            self.assertEqual(attr.name, '')
            self.assertFalse(os.path.isfile(file_path))


class EventDetailPlaceTest(TestCase):
    """ Testes edição de local de evento nos detalhes de evento pela view. """
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
        self.user = User.objects.get(username="flavia@in2web.com.br")

    def _login(self):
        """ Realiza login. """
        self.client.force_login(self.user)
        self._switch_context()

    def _get_active_organization(self):
        """ Resgata organização ativa no contexto do login. """
        return account.get_organization(self.client.request().wsgi_request)

    def _switch_context(self, group=Member.ADMIN):
        """ Muda organização do contexto de login. """
        organization = self._get_active_organization()
        other = Organization.objects.exclude(pk=organization.pk).filter(
            members__person=self.user.person,
            members__group=group
        ).first()
        url = reverse('event:organization-switch')
        self.client.post(url, {'organization-context-pk': other.pk})

    def _get_url(self, pk=None):
        """ Recupera URL. """
        if not pk:
            event = self._get_event()
            pk = event.pk

        return reverse('event:event-detail', kwargs={'pk': pk})

    # noinspection PyMethodMayBeStatic
    def _get_event(self):
        """ Recupera instância de evento. """
        return Event.objects.get(slug='encontro-de-lideres-2017')

    def test_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        response = self.client.get(self._get_url(1), follow=True)

        redirect_url = reverse('front:login')
        redirect_url += '?next='
        redirect_url += self._get_url(1)
        self.assertRedirects(response, redirect_url)

    def test_200(self):
        """ Testa se está tudo ok com view com submissão GET. """
        self._login()
        response = self.client.get(self._get_url())
        self.assertEqual(response.status_code, 200)

    def test_upload_place(self):
        """ Testa atualização de local de evento. """
        self._login()
        event = self._get_event()
        place = event.place

        organization = event.organization
        other_place = organization.places.exclude(pk=place.pk).first()
        assert other_place is not None

        # Envia outro local para atualização
        response = self.client.post(self._get_url(), data={
            'submit_type': 'update_place',
            'place': other_place.pk
        }, follow=True)
        self.assertContains(response, 'Local atualizado com sucesso.')

        # Verifica update
        event = self._get_event()
        self.assertNotEqual(event.place.pk, place.pk)

        # Envia nada para atualização de local
        response = self.client.post(self._get_url(), data={
            'submit_type': 'update_place',
            'place': ''
        }, follow=True)
        self.assertContains(response, 'Local atualizado com sucesso.')

        # Verifica update
        event = self._get_event()
        self.assertIsNone(event.place)


class EventDetailSocialMediaTest(TestCase):
    """
    Testes edição de informações sociais nos detalhes de evento pela view.
    """
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

    def _login(self):
        """ Realiza login """
        self.client.force_login(self.user)

    def _get_url(self, pk=None):
        """ Recupera URL """
        if not pk:
            event = self._get_event()
            pk = event.pk

        return reverse('event:event-detail', kwargs={'pk': pk})

    # noinspection PyMethodMayBeStatic
    def _get_event(self):
        """ Recupera instância de evento. """
        return Event.objects.get(slug='a-arte-de-usar-linux')

    def test_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        response = self.client.get(self._get_url(), follow=True)

        redirect_url = reverse('front:login')
        redirect_url += '?next='
        redirect_url += self._get_url()
        self.assertRedirects(response, redirect_url)

    def test_200(self):
        """ Testa se está tudo ok com view com submissão GET. """
        self._login()
        response = self.client.get(self._get_url())
        self.assertEqual(response.status_code, 200)

    def test_update_social_media(self):
        """ Testa atualização de social media. """
        self._login()
        event = self._get_event()
        place = event.place

        organization = event.organization
        other_place = organization.places.exclude(pk=place.pk).first()
        assert other_place is not None

        # Envia outro local para atualização
        response = self.client.post(self._get_url(), data={
            'website': 'http://seoresultados.com',
            'facebook': 'https://facebook.com/seoresultados',
            'twitter': 'https://twitter.com/seoresultados',
            'linkedin': 'https://linkedin.com/seoresultados',
            'skype': 'seoresultados',
            'submit_type': 'update_social_media',
        }, follow=True)

        self.assertContains(
            response,
            'Informações sociais atualizadas com sucesso'
        )
