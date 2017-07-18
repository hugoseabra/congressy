""" Testes de aplicação com `Info` - Formulários. """
import os
import shutil

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import six

from gatheros_event.forms import (
    Info4ImagesForm,
    InfoMainImageForm,
    InfoTextForm,
    InfoVideoForm,
)
from gatheros_event.models import Event, Info


class BaseInfoFormTest(TestCase):
    """ Classe base para formulário de informação de evento. """
    fixtures = [
        '007_organization',
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
            'images',
            'info'
        )
        self.persisted_path = 'event'
        self._clear_uploaded_dir()

    # noinspection PyMethodMayBeStatic
    def _get_event(self):
        return Event.objects.get(slug='streaming-de-sucesso')

    # noinspection PyMethodMayBeStatic
    def _get_info(self):
        event = self._get_event()
        return event.info

    # noinspection PyMethodMayBeStatic
    def _clear_uploaded_dir(self):
        info = self._get_info()
        path = os.path.join(
            settings.MEDIA_ROOT,
            self.persisted_path,
            str(info.event.pk)
        )
        if os.path.isdir(path):
            shutil.rmtree(path)

    def tearDown(self):
        """ Excluir arquivos enviados. """
        self._clear_uploaded_dir()


class InfoTextFormTest(BaseInfoFormTest):
    """ Testes de formulário de `Info` para somente texto. """

    def test_new_info(self):
        """ Testa criação de nova `Info`. """
        info = self._get_info()
        info.delete()

        event = self._get_event()
        data = {
            'event': event.pk,
            'description_html': '<p style="color:red>Some text</p>',
            'config_type': Info.CONFIG_TYPE_TEXT_ONLY,
        }

        form = InfoTextForm(data=data)
        self.assertTrue(form.is_valid())
        form.save()

        event = self._get_event()
        info = event.info
        self.assertIsInstance(info, Info)
        self.assertEqual(info.config_type, Info.CONFIG_TYPE_TEXT_ONLY)


class Info4ImagesFormTest(BaseInfoFormTest):
    """ Testes de formulário de `Info` para 4 imagens. """

    def test_new_info(self):
        """ Testa criação de nova `Info`. """
        info = self._get_info()
        assert info is not None

        file_names = {
            'image1': 'image1.jpg',
            'image2': 'image2.jpg',
            'image3': 'image3.jpg',
            'image4': 'image4.jpg',
        }

        file_dict = {}
        for field_name, file_name in six.iteritems(file_names):
            assert hasattr(info, field_name)
            attr = getattr(info, field_name)

            # Campo ImageFile deve estar vazio
            self.assertEqual(attr.name, '')

            file_path = os.path.join(self.file_base_path, file_name)
            persited_name = os.path.join(
                self.persisted_path,
                str(info.event_id),
                file_name
            )

            file = open(file_path, 'rb')
            file_dict[field_name] = SimpleUploadedFile(
                persited_name,
                file.read(),
                'image/jpeg'
            )

        data = {
            'event': info.event_id,
            'description_html': '<p style="color:red>Some text</p>',
            'config_type': Info.CONFIG_TYPE_4_IMAGES,
        }
        form = Info4ImagesForm(instance=info, data=data, files=file_dict)
        self.assertTrue(form.is_valid())
        form.save()

        info = self._get_info()
        self.assertEqual(info.config_type, Info.CONFIG_TYPE_4_IMAGES)

        for field_name, file_name in six.iteritems(file_names):
            assert hasattr(info, field_name)
            attr = getattr(info, field_name)
            file_path = os.path.join(
                self.persisted_path,
                str(info.event.pk),
                file_name
            )

            # Campo ImageFile deve ter o arquivo enviado.
            self.assertEqual(attr.name, file_path)
            self.assertTrue(os.path.isfile(os.path.join(
                settings.MEDIA_ROOT,
                file_path
            )))


class InfoMainImageFormTest(BaseInfoFormTest):
    """ Testes de formulário de `Info` para imagem principal. """

    def test_new_info(self):
        """ Testa criação de nova `Info`. """
        info = self._get_info()
        assert info is not None

        file_names = {
            'image_main': 'image_main.jpg',
        }

        file_dict = {}
        for field_name, file_name in six.iteritems(file_names):
            assert hasattr(info, field_name)
            attr = getattr(info, field_name)

            # Campo ImageFile deve estar vazio
            self.assertEqual(attr.name, '')

            file_path = os.path.join(self.file_base_path, file_name)
            persited_name = os.path.join(
                self.persisted_path,
                str(info.event_id),
                file_name
            )

            file = open(file_path, 'rb')
            file_dict[field_name] = SimpleUploadedFile(
                persited_name,
                file.read(),
                'image/jpeg'
            )

        data = {
            'event': info.event_id,
            'description_html': '<p style="color:red>Some text</p>',
            'config_type': Info.CONFIG_TYPE_MAIN_IMAGE,
        }
        form = InfoMainImageForm(instance=info, data=data, files=file_dict)
        self.assertTrue(form.is_valid())
        form.save()

        info = self._get_info()
        self.assertEqual(info.config_type, Info.CONFIG_TYPE_MAIN_IMAGE)

        for field_name, file_name in six.iteritems(file_names):
            assert hasattr(info, field_name)
            attr = getattr(info, field_name)
            file_path = os.path.join(
                self.persisted_path,
                str(info.event.pk),
                file_name
            )

            # Campo ImageFile deve ter o arquivo enviado.
            self.assertEqual(attr.name, file_path)
            self.assertTrue(os.path.isfile(os.path.join(
                settings.MEDIA_ROOT,
                file_path
            )))


class InfoVideoFormTest(BaseInfoFormTest):
    """ Testes de formulário de `Info` para vídeo. """

    def test_new_info(self):
        """ Testa criação de nova `Info`. """
        info = self._get_info()
        assert info is not None

        data = {
            'event': info.event.pk,
            'description_html': '<p style="color:red>Some text</p>',
            'config_type': Info.CONFIG_TYPE_VIDEO,
            'youtube_video': 'https://www.youtube.com/embed/jbVpFUGCw1o'
        }

        form = InfoVideoForm(instance=info, data=data)
        self.assertTrue(form.is_valid())
        form.save()

        info = self._get_info()
        self.assertEqual(info.config_type, Info.CONFIG_TYPE_VIDEO)

    def test_video_youtube(self):
        """
        Testando o recurso do modelo tratar as diferentes urls do youtube
        """

        def save_info(cls, youtube_video):
            info = cls._get_info()
            assert info is not None

            data = {
                'event': info.event.pk,
                'description_html': '<p style="color:red>Some text</p>',
                'config_type': Info.CONFIG_TYPE_VIDEO,
                'youtube_video': youtube_video
            }

            form = InfoVideoForm(instance=info, data=data)
            cls.assertTrue(form.is_valid())
            return form.save()

        """
        Urls no padrão: https://www.youtube.com/watch?v=GFmzLy6z8W8
        """
        instance = save_info(
            self,
            'https://www.youtube.com/watch?v=GFmzLy6z8W8'
        )
        self.assertEqual(
            instance.youtube_video,
            'https://www.youtube.com/embed/GFmzLy6z8W8'
        )

        """
        Urls no padrão: https://www.youtube.com/watch?v=GFmzLy6z8W8
        """
        instance = save_info(
            self,
            'https://youtu.be/GFmzLy6z8W8'
        )
        self.assertEqual(
            instance.youtube_video,
            'https://www.youtube.com/embed/GFmzLy6z8W8'
        )

        """
        Imgagem do vídeo
        """
        self.assertEqual(
            instance.youtube_image,
            'https://img.youtube.com/vi/GFmzLy6z8W8/0.jpg'
        )
