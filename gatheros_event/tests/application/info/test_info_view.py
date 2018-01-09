""" Testes de aplicação com `Event` - Formulários pela view. """
import os
import shutil

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import six

from gatheros_event.models import Event, Info


class EventInfoTest(TestCase):
    """ Testes de formulário de informações de evento pela view. """
    fixtures = [
        'kanu_locations_city_test',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
        '009_place',
        '010_event',
        '011_info',
    ]

    def setUp(self):
        self.file_base_path = os.path.join(
            settings.BASE_DIR,
            'gatheros_event',
            'tests',
            'fixtures',
            'media',
            'info'
        )
        self.user = User.objects.get(username="lucianasilva@gmail.com")

    def _login(self):
        """ Realiza login. """
        self.client.force_login(self.user)

    def _get_url(self, pk=None, **kwargs):
        """ Resgata URL. """
        if not pk:
            event = self._get_event()
            pk = event.pk
        kwargs.update({
            'pk': pk
        })
        return reverse('event:event-info', kwargs=kwargs)

    # noinspection PyMethodMayBeStatic
    def _get_event(self):
        """ Resgata instância de Event. """
        return Event.objects.get(slug='cafe-expresso-como-preparar')

    def tearDown(self):
        """ Limpa dados enviados nos testes se ainda estiverem lá. """
        event = self._get_event()
        path = os.path.join(
            settings.MEDIA_ROOT,
            'event',
            str(event.pk)
        )
        if os.path.isdir(path):
            shutil.rmtree(path)

    def test_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        response = self.client.get(self._get_url(pk=1), follow=True)

        redirect_url = reverse('public:login')
        redirect_url += '?next=' + reverse('event:event-list')
        self.assertRedirects(response, redirect_url)

    def test_200(self):
        """ Testa se está tudo ok com view com submissão GET. """
        self._login()
        response = self.client.get(self._get_url())
        self.assertEqual(response.status_code, 200)

    def test_text(self):
        """ Testa exibição somente texto. """
        self._login()
        event = self._get_event()
        data = {
            'event': event.pk,
            'description_html': '<p style="color:red>Some text</p>',
            'config_type': Info.CONFIG_TYPE_TEXT_ONLY,
        }

        response = self.client.post(self._get_url(), data=data, follow=True)
        self.assertContains(
            response,
            "Informações de capa atualizadas com sucesso."
        )

    def test_4_images(self):
        """ Testa exibição de 4 imagens. """
        self._login()
        file_names = {
            'image1': 'image1.jpg',
            'image2': 'image2.jpg',
            'image3': 'image3.jpg',
            'image4': 'image4.jpg',
        }

        data = {}
        for field_name, file_name in six.iteritems(file_names):
            file_path = os.path.join(self.file_base_path, file_name)
            file = open(file_path, 'rb')
            data[field_name] = file

        event = self._get_event()
        data['event'] = event.pk
        data['description_html'] = '<p style="color:red>Some text</p>'
        data['config_type'] = Info.CONFIG_TYPE_4_IMAGES

        response = self.client.post(self._get_url(), data=data, follow=True)
        self.assertContains(
            response,
            "Informações de capa atualizadas com sucesso."
        )

    def test_main_image(self):
        """ Testa exibição de imagem principal. """
        self._login()
        file_names = {
            'main_image': 'image_main.jpg',
        }

        data = {}
        for field_name, file_name in six.iteritems(file_names):
            file_path = os.path.join(self.file_base_path, file_name)
            file = open(file_path, 'rb')
            data[field_name] = file

        event = self._get_event()
        data['event'] = event.pk
        data['description_html'] = '<p style="color:red>Some text</p>'
        data['config_type'] = Info.CONFIG_TYPE_MAIN_IMAGE

        response = self.client.post(self._get_url(), data=data, follow=True)
        self.assertContains(
            response,
            "Informações de capa atualizadas com sucesso."
        )

    def test_video_get(self):
        """
        Testa o carregamento da página do vídeo
        """
        self._login()
        response = self.client.get(self._get_url(), data={'type': 'video'})
        self.assertContains(response, "URL do Youtube")

    def test_video(self):
        """ Testa exibição de vídeo. """
        self._login()
        event = self._get_event()
        data = {
            'event': event.pk,
            'description_html': '<p style="color:red>Some text</p>',
            'config_type': Info.CONFIG_TYPE_VIDEO,
            'youtube_video': 'https://www.youtube.com/embed/jbVpFUGCw1o'
        }

        response = self.client.post(self._get_url(), data=data, follow=True)
        self.assertContains(
            response,
            "Informações de capa atualizadas com sucesso."
        )
